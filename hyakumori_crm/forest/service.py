from typing import Iterator, Union

from django.core.exceptions import ValidationError
from django.db.models import F
from django.db.models.expressions import RawSQL
from django.utils.translation import gettext_lazy as _

from .schemas import ForestFilter, CustomerDefaultInput, CustomerContactDefaultInput
from ..crm.models import (
    Forest,
    ForestCustomer,
    Customer,
    CustomerContact,
    ForestCustomerContact,
    Contact,
)


def get_forest_by_pk(pk):
    try:
        return Forest.objects.get(pk=pk)
    except (Forest.DoesNotExist, ValidationError):
        raise ValueError(_("Forest not found"))


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
    query = filters.qs if filters else Forest.objects.all()
    total = query.count()
    forests = query.order_by("-updated_at", "-created_at")[offset: offset + per_page]
    return forests, total


def update(forest: Forest, forest_in: dict):
    forest.cadastral = forest_in["cadastral"]
    forest.contracts = forest_in["contracts"]
    forest.save()
    return forest


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
                 crm_forestcustomer.attributes->>'default'
        """,
        {"pk": pk},
    ).prefetch_related("customercontact_set__contact")

    return qs


def get_customer_contacts_of_forest(pk):
    return (
        Contact.objects.filter(
            customercontact__attributes__contact_type="FOREST",
            customercontact__forestcustomercontact__forestcustomer__forest_id=pk,
        )
            .annotate(
            is_basic=F("customercontact__is_basic")
        )  # actualy its always False, why did we retrieve it?
            .annotate(customer_id=F("customercontact__customer_id"))
            .annotate(
            default=RawSQL(
                "crm_forestcustomercontact.attributes->>'default'", params=[]
            )
        )
            .annotate(cc_attrs=F("customercontact__attributes"))
    )


def set_default_customer(data: CustomerDefaultInput):
    fc = ForestCustomer.objects.filter(
        forest_id=data.forest.id, customer_id=data.customer_id
    ).update(attributes={"default": data.default})
    data.forest.save(update_fields=["updated_at"])
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


def get_all_forest_csv_data():
    return Forest.objects.all().distinct("id").annotate(forest_id=F("id")).annotate(
        customer_name_kana=RawSQL(
            """
            select array_to_string(array_agg(concat_ws(' ', cc2.name_kana->>'last_name', cc2.name_kana->>'first_name')), '; ')
            from crm_customer c
            inner join crm_forestcustomer cf on c.id = cf.customer_id
            inner join crm_customercontact cc on c.id = cc.customer_id
            inner join crm_contact cc2 on cc.contact_id = cc2.id
            where crm_forest.id = cf.forest_id and cc.is_basic = true
            """,
            params=[]
        )).annotate(
        customer_name_kanji=RawSQL(
            """
            select array_to_string(array_agg(concat_ws(' ', cc4.name_kanji->>'last_name', cc4.name_kanji->>'first_name')), '; ')
            from crm_customer c
            inner join crm_forestcustomer cf on c.id = cf.customer_id
            inner join crm_customercontact cc3 on c.id = cc3.customer_id
            inner join crm_contact cc4 on cc3.contact_id = cc4.id
            where crm_forest.id = cf.forest_id and cc3.is_basic = true
            """,
            params=[]
        )).annotate(
        customer_internal_id=F("forestcustomer__customer__internal_id"))


def get_specific_forest_csv_data(forest_ids):
    return Forest.objects.filter(id__in=forest_ids).distinct("id").annotate(forest_id=F("id")).annotate(
        customer_name_kana=RawSQL(
            """
            select array_to_string(array_agg(concat_ws(' ', cc2.name_kana->>'last_name', cc2.name_kana->>'first_name')), '; ')
            from crm_customer c
            inner join crm_forestcustomer cf on c.id = cf.customer_id
            inner join crm_customercontact cc on c.id = cc.customer_id
            inner join crm_contact cc2 on cc.contact_id = cc2.id
            where crm_forest.id = cf.forest_id and cc.is_basic = true
            """,
            params=[]
        )).annotate(
        customer_name_kanji=RawSQL(
            """
            select array_to_string(array_agg(concat_ws(' ', cc4.name_kanji->>'last_name', cc4.name_kanji->>'first_name')), '; ')
            from crm_customer c
            inner join crm_forestcustomer cf on c.id = cf.customer_id
            inner join crm_customercontact cc3 on c.id = cc3.customer_id
            inner join crm_contact cc4 on cc3.contact_id = cc4.id
            where crm_forest.id = cf.forest_id and cc3.is_basic = true
            """,
            params=[]
        )).annotate(
        customer_internal_id=F("forestcustomer__customer__internal_id"))


def forest_csv_data_mapping(forest):
    return [
        forest.forest_id,
        forest.internal_id,
        forest.cadastral.get('prefecture'),
        forest.cadastral.get('municipality'),
        forest.cadastral.get('sector'),
        forest.cadastral.get('subsector'),
        forest.land_attributes.get('地番本番'),
        forest.land_attributes.get('地番支番'),
        forest.land_attributes.get('地目'),
        forest.land_attributes.get('林班'),
        forest.land_attributes.get('小班'),
        forest.land_attributes.get('区画'),
        forest.customer_name_kanji,
        forest.customer_name_kana,
        forest.contracts[0].get('status'),
        forest.contracts[0].get('start_date'),
        forest.contracts[0].get('end_date'),
        forest.contracts[1].get('status'),
        forest.contracts[1].get('start_date'),
        forest.contracts[1].get('end_date'),
        forest.contracts[2].get('status'),
        forest.contracts[2].get('start_date'),
        forest.contracts[2].get('end_date'),
        forest.tags.get('danchi'),
        forest.tags.get('manage_type'),
        forest.forest_attributes.get('地番面積_ha'),
        forest.forest_attributes.get('面積_ha'),
        forest.forest_attributes.get('面積_m2'),
        forest.forest_attributes.get('平均傾斜度'),
        forest.forest_attributes.get('第1林相ID'),
        forest.forest_attributes.get('第1林相名'),
        forest.forest_attributes.get('第1Area'),
        forest.forest_attributes.get('第1面積_ha'),
        forest.forest_attributes.get('第1立木本'),
        forest.forest_attributes.get('第1立木密'),
        forest.forest_attributes.get('第1平均樹'),
        forest.forest_attributes.get('第1樹冠長'),
        forest.forest_attributes.get('第1平均DBH'),
        forest.forest_attributes.get('第1合計材'),
        forest.forest_attributes.get('第1ha材積'),
        forest.forest_attributes.get('第1収量比'),
        forest.forest_attributes.get('第1相対幹'),
        forest.forest_attributes.get('第1形状比'),
        forest.forest_attributes.get('第2林相ID'),
        forest.forest_attributes.get('第2林相名'),
        forest.forest_attributes.get('第2Area'),
        forest.forest_attributes.get('第2面積_ha'),
        forest.forest_attributes.get('第2立木本'),
        forest.forest_attributes.get('第2立木密'),
        forest.forest_attributes.get('第2平均樹'),
        forest.forest_attributes.get('第2樹冠長'),
        forest.forest_attributes.get('第2平均DBH'),
        forest.forest_attributes.get('第2合計材'),
        forest.forest_attributes.get('第2ha材積'),
        forest.forest_attributes.get('第2収量比'),
        forest.forest_attributes.get('第2相対幹'),
        forest.forest_attributes.get('第2形状比'),
        forest.forest_attributes.get('第3林相ID'),
        forest.forest_attributes.get('第3林相名'),
        forest.forest_attributes.get('第3Area'),
        forest.forest_attributes.get('第3面積_ha'),
        forest.forest_attributes.get('第3立木本'),
        forest.forest_attributes.get('第3立木密'),
        forest.forest_attributes.get('第3平均樹'),
        forest.forest_attributes.get('第3樹冠長'),
        forest.forest_attributes.get('第3平均DBH'),
        forest.forest_attributes.get('第3合計材'),
        forest.forest_attributes.get('第3ha材積'),
        forest.forest_attributes.get('第3収量比'),
        forest.forest_attributes.get('第3相対幹'),
        forest.forest_attributes.get('第3形状比')
    ]
