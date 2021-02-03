import csv
import itertools
from collections import defaultdict
from typing import Iterator, Union

import pydantic
from django.core.exceptions import ValidationError
from django.db import OperationalError, connection
from django.db.models import F, OuterRef, Subquery, Count
from django.db.models.expressions import RawSQL
from django.db import ProgrammingError
from django.utils.translation import gettext_lazy as _
from querybuilder.query import Query, QueryWindow
from querybuilder.fields import RowNumberField

from ..cache.forest import refresh_customer_forest_cache
from ..core.decorators import errors_wrapper
from ..crm.common.constants import (
    FOREST_CADASTRAL,
    FOREST_LAND_ATTRIBUTES,
    FOREST_OWNER_INFO,
    FOREST_CONTRACT,
    FOREST_ATTRIBUTES,
)
from ..crm.models import (
    Forest,
    ForestCustomer,
    Customer,
    CustomerContact,
    ForestCustomerContact,
    Contact,
)
from ..crm.schemas.contract import ContractType as ContractTypeEnum

from .schemas import (
    CustomerDefaultInput,
    CustomerContactDefaultInput,
    ContractUpdateInput,
    ForestInput,
    ForestCsvInput,
    ForestContractStatusBulkUpdate,
)
from .filters import ForestFilter


def get_forest_by_pk(pk):
    try:
        return Forest.objects.get(pk=pk)
    except (Forest.DoesNotExist, ValidationError):
        raise ValueError(_("Forest not found"))


def get_forests_tag_by_ids(ids):
    with connection.cursor() as cursor:
        cursor.execute(
            "select distinct jsonb_object_keys(tags) from crm_forest where id in %(ids)s",
            {"ids": tuple(ids)},
        )
        tags = cursor.fetchall()
    return list(itertools.chain(*tags))


def get_customer_of_forest(pk, customer_pk):
    try:
        return (
            ForestCustomer.objects.select_related("customer")
            .get(customer_id=customer_pk, forest_id=pk)
            .customer
        )
    except (
        ForestCustomer.DoesNotExist,
        Customer.DoesNotExist,
        ValidationError,
    ):
        raise ValueError(_("Customer not found"))


def get_contract_by_type(contracts, contract_type):
    result = next(
        iter(
            [
                contract
                for contract in contracts
                if contract.get("type") == contract_type
            ]
        ),
        None,
    )
    if result is None:
        result = {"type": None, "status": None, "start_date": None, "end_date": None}
    return result


def map_forests_contracts(forest, contract_types):
    contract = forest.contracts[0]
    fsc = forest.contracts[-1]

    forest.contracts = {
        "contract_type": contract.get("type"),
        "contract_status": contract.get("status"),
        "contract_start_date": contract.get("start_date"),
        "contract_end_date": contract.get("end_date"),
        "fsc_status": fsc.get("status"),
        "fsc_start_date": fsc.get("start_date"),
    }

    return forest


def map_input_to_contracts(forest, contracts_in: ContractUpdateInput):
    update_contracts = []
    for contract in forest.contracts:
        if contract.get("type") == ContractTypeEnum.fsc:
            continue
        if contract.get("type") == contracts_in.contract_type:
            contract["start_date"] = contracts_in.contract_start_date
            contract["end_date"] = contracts_in.contract_end_date
            contract["status"] = contracts_in.contract_status
            update_contracts.append(contract)

    if len(update_contracts) == 0:
        update_contracts.append(
            dict(
                type=contracts_in.contract_type,
                status=contracts_in.contract_status,
                start_date=contracts_in.contract_start_date,
                end_date=contracts_in.contract_end_date,
            )
        )

    update_contracts.append(
        {
            "type": ContractTypeEnum.fsc.value,
            "status": contracts_in.fsc_status,
            "start_date": contracts_in.fsc_start_date,
        }
    )

    return update_contracts


def get_forests_by_condition(
    page_num: int = 1,
    per_page: int = 10,
    pre_per_page: Union[int, None] = None,
    order_by: Union[Iterator, None] = None,
    filters: Union[ForestFilter, None] = None,
):
    offset = (pre_per_page or per_page) * (page_num - 1)
    if not order_by:
        order_by = []
    if filters and not filters.is_valid():
        return [], 0
    query = filters.qs
    total = query.count()
    forests = query.order_by("internal_id")[offset : offset + per_page]
    return forests, total


def update_basic_info(forest: Forest, forest_in: ForestInput):
    forest.cadastral = forest_in.cadastral.dict()
    forest.land_attributes["地番本番"] = forest_in.land_attributes.get("地番本番")
    forest.land_attributes["地番支番"] = forest_in.land_attributes.get("地番支番")
    forest.contracts = map_input_to_contracts(forest, forest_in.contracts)
    forest.save(
        update_fields=["cadastral", "contracts", "land_attributes", "updated_at"]
    )
    return forest


def update_forest_tags(data: dict):
    ids = data.get("ids")
    tag_key = data.get("key")
    new_value = data.get("value")
    Forest.objects.filter(id__in=ids).update(
        tags=RawSQL("tags || jsonb_build_object(%s, %s)", params=[tag_key, new_value])
    )


def update_owners(owner_pks_in):
    forest = owner_pks_in.forest

    # deleting
    forestcustomers = ForestCustomer.objects.filter(
        customer_id__in=owner_pks_in.deleted, forest_id=forest.pk
    )
    CustomerContact.objects.filter(
        forestcustomercontact__forestcustomer_id__in=forestcustomers.values("id")
    ).delete()
    forestcustomers.delete()

    # adding
    added_forest_customers = []
    for added_owner_pk in owner_pks_in.added:
        forest_customer = ForestCustomer(
            customer_id=added_owner_pk, forest_id=forest.pk,
        )
        added_forest_customers.append(forest_customer)

    ForestCustomer.objects.bulk_create(added_forest_customers)
    forest.save(update_fields=["updated_at"])
    forest.refresh_from_db()

    refresh_customer_forest_cache(forest_ids=[str(forest.id)])

    return forest


def get_forest_customers(pk):
    qs = Customer.objects.raw(
        """
        with self_contact as (
            select customer_id from crm_contact A0
            join crm_customercontact A1 on A0.id = A1.contact_id
            where A1.is_basic = true and A0.deleted is null
            and A1.deleted is null
        )
        select crm_customer.*,
               count(A0.id) as forests_count,
               crm_forestcustomer.attributes->>'default' as default
        from crm_customer
        join self_contact
            on self_contact.customer_id = crm_customer.id
        join crm_forestcustomer on crm_customer.id = crm_forestcustomer.customer_id
        left outer join crm_forestcustomer A0 on crm_customer.id = A0.customer_id
        where crm_forestcustomer.forest_id = %(pk)s::uuid
        group by crm_customer.id,
                 crm_forestcustomer.attributes->>'default',
                 crm_forestcustomer.created_at
        order by crm_forestcustomer.created_at
        """,
        {"pk": pk},
    ).prefetch_related("customercontact_set__contact")

    return qs


def get_customer_contacts_of_forest(pk):
    cc = CustomerContact.objects.filter(is_basic=True, contact=OuterRef("pk"))
    cc_business_id = CustomerContact.objects.filter(
        is_basic=True, contact=OuterRef("pk")
    ).annotate(business_id=F("customer__business_id"))
    cc_forests_count = (
        CustomerContact.objects.filter(is_basic=True, contact=OuterRef("pk"))
        .values("id", "customer_id")
        .annotate(forests_count=Count("customer__forestcustomer"))
    )
    return (
        Contact.objects.filter(
            customercontact__forestcustomercontact__forestcustomer__forest_id=pk,
            customercontact__is_basic=False,
        )
        .annotate(customer_id=F("customercontact__customer_id"))
        .annotate(
            default=RawSQL(
                "crm_forestcustomercontact.attributes->>'default'", params=[]
            )
        )
        .annotate(cc_attrs=F("customercontact__attributes"))
        .annotate(owner_customer_id=Subquery(cc.values("customer_id")[:1]))
        .annotate(business_id=Subquery(cc_business_id.values("business_id")[:1]))
        .annotate(forests_count=Subquery(cc_forests_count.values("forests_count")[:1]))
    )


def set_default_customer(data: CustomerDefaultInput):
    fc = ForestCustomer.objects.filter(
        forest_id=data.forest.id, customer_id=data.customer_id
    ).update(attributes={"default": data.default})
    data.forest.save(update_fields=["updated_at"])
    refresh_customer_forest_cache(forest_ids=[str(data.forest.id)])
    return data.forest


def set_default_customer_contact(data: CustomerContactDefaultInput):
    fc = ForestCustomerContact.objects.filter(
        forestcustomer__forest_id=data.forest.id,
        forestcustomer__customer_id=data.customer_id,
        customercontact__customer_id=data.customer_id,
        customercontact__contact_id=data.contact_id,
    ).update(attributes={"default": data.default})
    data.forest.save(update_fields=["updated_at"])
    return data.forest


def update_forest_memo(forest, memo):
    _memo = forest.attributes.get("memo")
    _updated = False

    if _memo != memo:
        forest.attributes["memo"] = memo
        forest.save()
        _updated = True

    return forest, _updated


def csv_headers():
    header = ["内部ID", "土地管理ID"]
    return list(
        itertools.chain(
            header,
            FOREST_CADASTRAL,
            FOREST_LAND_ATTRIBUTES,
            FOREST_OWNER_INFO,
            FOREST_CONTRACT,
            [_("Tag")],
            FOREST_ATTRIBUTES,
        )
    )


def get_forests_for_csv(forest_ids: list = None):
    forestcustomercontact_rank_query = Query().from_table(
        ForestCustomerContact,
        [
            "forestcustomer_id",
            "customercontact_id",
            RowNumberField(
                alias="rank",
                over=QueryWindow()
                .order_by(
                    "coalesce(attributes->>'default', 'false')",
                    desc=True,
                    nulls_last=True,
                )
                .order_by("created_at")
                .partition_by("forestcustomer_id"),
            ),
        ],
    )

    forestcustomer_rank_query = Query().from_table(
        ForestCustomer,
        [
            "id",
            "forest_id",
            "customer_id",
            RowNumberField(
                alias="rank",
                over=QueryWindow()
                .order_by(
                    "coalesce(attributes->>'default', 'false')",
                    desc=True,
                    nulls_last=True,
                )
                .order_by("created_at")
                .partition_by("forest_id"),
            ),
        ],
    )
    forestcustomer_query = (
        Query()
        .from_table("fc_rank", fields=["forest_id"])
        .join(Customer, condition="crm_customer.id = fc_rank.customer_id")
        .join(
            CustomerContact,
            condition="crm_customercontact.customer_id = crm_customer.id "
            "and crm_customercontact.is_basic = true",
        )
        .join(
            Contact,
            condition="crm_customercontact.contact_id = crm_contact.id",
            fields=[
                {"customer_name_kanji": "name_kanji"},
                {"customer_name_kana": "name_kana"},
                {"customer_address": "address"},
            ],
        )
        .join(
            "fcc",
            condition="fc_rank.id = fcc.forestcustomer_id and fcc.rank = 1",
            join_type="LEFT JOIN",
        )
        .join(
            {"contact_cc": CustomerContact},
            condition="contact_cc.id = fcc.customercontact_id "
            "and contact_cc.id != crm_customercontact.id",
            join_type="LEFT JOIN",
        )
        .join(
            {"contact_c": Contact},
            join_type="LEFT JOIN",
            condition="contact_cc.contact_id = contact_c.id",
            fields=[
                {"contact_name_kanji": "name_kanji"},
                {"contact_name_kana": "name_kana"},
                {"contact_address": "address"},
            ],
        )
        .where(**{"fc_rank.rank": 1})
    )
    queryset = (
        Query()
        .with_query(forestcustomer_query, alias="fc")
        .with_query(forestcustomercontact_rank_query, alias="fcc")
        .with_query(forestcustomer_rank_query, alias="fc_rank")
        .from_table(
            {"f": Forest},
            fields=[
                "land_attributes",
                "cadastral",
                "id",
                "internal_id",
                "tags",
                "forest_attributes",
                "contracts",
            ],
        )
        .join(
            "fc",
            condition="fc.forest_id = f.id",
            join_type="LEFT JOIN",
            fields=[
                "customer_name_kanji",
                "customer_name_kana",
                "customer_address",
                "contact_name_kanji",
                "contact_name_kana",
                "contact_address",
            ],
        )
    )
    if forest_ids is not None and len(forest_ids) > 0:
        queryset = queryset.where(id__in=forest_ids)
    try:
        return queryset.select()
    except ProgrammingError:
        return []


def parse_tags_for_csv(tags: dict):
    if tags is None or len(tags.keys()) == 0:
        return None
    else:
        result = ""
        for (k, v) in tags.items():
            if k is not None and v is not None:
                result += f"{k}:{v}; "
        # remove the last semicolon
        return result[0 : len(result) - 2]


def forest_csv_data_mapping(forest):
    return [
        forest["id"],
        forest["internal_id"],
        forest["cadastral"].get("prefecture"),
        forest["cadastral"].get("municipality"),
        forest["cadastral"].get("sector"),
        forest["cadastral"].get("subsector"),
        forest["land_attributes"].get("地番本番"),
        forest["land_attributes"].get("地番支番"),
        forest["land_attributes"].get("地目"),
        forest["land_attributes"].get("林班"),
        forest["land_attributes"].get("小班"),
        forest["land_attributes"].get("区画"),
        "\u3000".join(
            filter(
                lambda x: x,
                [
                    (forest.get("customer_name_kanji") or {}).get("last_name"),
                    (forest.get("customer_name_kanji") or {}).get("first_name"),
                ],
            )
        ),
        "\u3000".join(
            filter(
                lambda x: x,
                [
                    (forest.get("customer_name_kana") or {}).get("last_name"),
                    (forest.get("customer_name_kana") or {}).get("first_name"),
                ],
            )
        ),
        " ".join(
            filter(
                lambda x: x,
                [
                    (forest.get("customer_address") or {}).get("prefecture"),
                    (forest.get("customer_address") or {}).get("municipality"),
                    (forest.get("customer_address") or {}).get("sector"),
                ],
            )
        ),
        "\u3000".join(
            filter(
                lambda x: x,
                [
                    (forest.get("contact_name_kanji") or {}).get("last_name"),
                    (forest.get("contact_name_kanji") or {}).get("first_name"),
                ],
            )
        ),
        "\u3000".join(
            filter(
                lambda x: x,
                [
                    (forest.get("contact_name_kana") or {}).get("last_name"),
                    (forest.get("contact_name_kana") or {}).get("first_name"),
                ],
            )
        ),
        " ".join(
            filter(
                lambda x: x,
                [
                    (forest.get("contact_address") or {}).get("prefecture"),
                    (forest.get("contact_address") or {}).get("municipality"),
                    (forest.get("contact_address") or {}).get("sector"),
                ],
            )
        ),
        forest["contracts"][0].get("type"),
        forest["contracts"][0].get("status"),
        f'"{forest["contracts"][0].get("start_date") or ""}"',
        f'"{forest["contracts"][0].get("end_date") or ""}"',
        forest["contracts"][-1].get("status"),
        f'"{forest["contracts"][-1].get("start_date") or ""}"',
        parse_tags_for_csv(forest["tags"]),
        forest["forest_attributes"].get("地番面積_ha"),
        forest["forest_attributes"].get("面積_ha"),
        forest["forest_attributes"].get("面積_m2"),
        forest["forest_attributes"].get("平均傾斜度"),
        forest["forest_attributes"].get("第1林相ID"),
        forest["forest_attributes"].get("第1林相名"),
        forest["forest_attributes"].get("第1Area"),
        forest["forest_attributes"].get("第1面積_ha"),
        forest["forest_attributes"].get("第1立木本"),
        forest["forest_attributes"].get("第1立木密"),
        forest["forest_attributes"].get("第1平均樹"),
        forest["forest_attributes"].get("第1樹冠長"),
        forest["forest_attributes"].get("第1平均DBH"),
        forest["forest_attributes"].get("第1合計材"),
        forest["forest_attributes"].get("第1ha材積"),
        forest["forest_attributes"].get("第1収量比"),
        forest["forest_attributes"].get("第1相対幹"),
        forest["forest_attributes"].get("第1形状比"),
        forest["forest_attributes"].get("第2林相ID"),
        forest["forest_attributes"].get("第2林相名"),
        forest["forest_attributes"].get("第2Area"),
        forest["forest_attributes"].get("第2面積_ha"),
        forest["forest_attributes"].get("第2立木本"),
        forest["forest_attributes"].get("第2立木密"),
        forest["forest_attributes"].get("第2平均樹"),
        forest["forest_attributes"].get("第2樹冠長"),
        forest["forest_attributes"].get("第2平均DBH"),
        forest["forest_attributes"].get("第2合計材"),
        forest["forest_attributes"].get("第2ha材積"),
        forest["forest_attributes"].get("第2収量比"),
        forest["forest_attributes"].get("第2相対幹"),
        forest["forest_attributes"].get("第2形状比"),
        forest["forest_attributes"].get("第3林相ID"),
        forest["forest_attributes"].get("第3林相名"),
        forest["forest_attributes"].get("第3Area"),
        forest["forest_attributes"].get("第3面積_ha"),
        forest["forest_attributes"].get("第3立木本"),
        forest["forest_attributes"].get("第3立木密"),
        forest["forest_attributes"].get("第3平均樹"),
        forest["forest_attributes"].get("第3樹冠長"),
        forest["forest_attributes"].get("第3平均DBH"),
        forest["forest_attributes"].get("第3合計材"),
        forest["forest_attributes"].get("第3ha材積"),
        forest["forest_attributes"].get("第3収量比"),
        forest["forest_attributes"].get("第3相対幹"),
        forest["forest_attributes"].get("第3形状比"),
    ]


def csv_column_to_dict(keys, values):
    return dict(zip(keys, values))


def dict_to_list(data: dict):
    return [{"key": key, "value": value} for key, value in data.items()]


def list_to_dict(data: list):
    result = {}
    for data in data:
        result[data.key] = data.value
    return result


def parse_csv_data_to_dict(row_data):
    new_forest = {}
    cadastral_keys = ["prefecture", "municipality", "sector", "subsector"]
    cadastral = []
    land_attributes = []
    contract_keys = [
        "contract_type",
        "contract_status",
        "contract_start_date",
        "contract_end_date",
        "fsc_status",
        "fsc_start_date",
    ]
    contract = []
    forest_attributes = []
    for i in range(len(row_data)):
        if i == 0:
            if row_data[i] and row_data[i][0] == "\ufeff":
                new_forest["id"] = row_data[i][1:]  # exluce BOM char
            else:
                new_forest["id"] = row_data[i]
        elif i == 1:
            new_forest["internal_id"] = row_data[i]
        elif 1 < i <= 5:
            cadastral.append(row_data[i])
        elif 5 < i <= 11:
            land_attributes.append(row_data[i])
        elif 17 < i <= 23:
            contract.append(row_data[i])
        elif i == 24:
            new_forest["tags"] = row_data[i]
        elif 24 < i <= len(row_data) - 1:
            forest_attributes.append(row_data[i])
    new_forest["cadastral"] = csv_column_to_dict(cadastral_keys, cadastral)
    new_forest["land_attributes"] = dict_to_list(
        csv_column_to_dict(FOREST_LAND_ATTRIBUTES, land_attributes)
    )
    new_forest["contracts"] = dict(zip(contract_keys, contract))
    new_forest["forest_attributes"] = dict_to_list(
        csv_column_to_dict(FOREST_ATTRIBUTES, forest_attributes)
    )
    return new_forest


def update_forest_csv(forest, data: ForestCsvInput):
    forest.cadastral = data.cadastral.dict()
    forest.land_attributes = list_to_dict(data.land_attributes)
    forest.contracts = map_input_to_contracts(forest, data.contracts)
    forest.tags = data.tags_json
    forest.forest_attributes = list_to_dict(data.forest_attributes)
    forest.save()


def csv_upload(fp):
    with open(fp, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        line_count = 0
        headers = csv_headers()
        for row in reader:
            if line_count == 0:
                line_count += 1
                if row != headers:
                    return {"errors": {"__root__": [_("Invalid csv file!")]}}
                continue
            row_data = parse_csv_data_to_dict(row)
            try:
                clean_forest = ForestCsvInput(**row_data)
            except pydantic.ValidationError as e:
                errors = defaultdict(list)
                for key, msgs in errors_wrapper(e.errors()).items():
                    if key == "__root__":
                        errors[key] = msgs
                    else:
                        try:
                            errors[csv_errors_map[key]].extend(msgs)
                        except KeyError:
                            errors[key].extend(msgs)

                return {"line": line_count + 1, "errors": errors}
            try:
                forest = Forest.objects.select_for_update(nowait=True).get(
                    pk=row_data["id"]
                )
            except (Forest.DoesNotExist, ValidationError):
                return {
                    "line": line_count + 1,
                    "errors": {"__root__": [_("Forest not found")]},
                }
            except OperationalError:
                return {
                    "errors": {
                        "__root__": ["Current resources are not ready for update!!"]
                    },
                }
            else:
                update_forest_csv(forest, clean_forest)
                line_count += 1
        if line_count == 0:
            return {"errors": {"__root__": [_("Invalid csv file!")]}}
        return line_count


csv_errors_map = {
    "id": "内部ID",
    "internal_id": "土地管理ID",
    "cadastral.prefecture": "都道府県",
    "cadastral.municipality": "市町村",
    "cadastral.sector": "大字",
    "cadastral.subsector": "字",
    "contracts.contract_type": "契約種類",
    "contracts.contract_status": "契約状況",
    "contracts.contract_start_date": "開始日",
    "contracts.contract_end_date": "終了日",
    "contracts.fsc_status": "FSC認証",
    "contracts.fsc_start_date": "FSC開始日",
    "land_attributes.0.__root__": "地番本番",
    "land_attributes.1.__root__": "地番支番",
    "tags": "タグ",
}


def bulk_update_forest_contact_status(data: ForestContractStatusBulkUpdate):
    return Forest.objects.filter(pk__in=data.pks).update(
        contracts=RawSQL(
            "jsonb_set(contracts, '{0,status}', %s)", params=[f'"{data.status.value}"']
        )
    )
