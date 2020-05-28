import uuid
import itertools
from typing import Iterator, Union
from uuid import UUID

from django.db import DataError, IntegrityError, connection
from django.db.models import Count, F, OuterRef, Q, Subquery
from django.db.models.expressions import RawSQL, Value
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _
from django_q.tasks import async_task
from querybuilder.query import Query

from hyakumori_crm.core.models import RawSQLField
from hyakumori_crm.crm.models import (
    Archive,
    Contact,
    Customer,
    CustomerContact,
    Forest,
    ForestCustomer,
    ForestCustomerContact,
)
from .filters import CustomerFilter
from .schemas import ContactType, CustomerInputSchema, ContactsInput
from ..cache.forest import refresh_customer_forest_cache


def get_customer_by_pk(pk):
    try:
        return Customer.objects.raw(
            """select crm_customer.*, count(A0.id) as forests_count
from crm_customer
left outer join crm_forestcustomer A0
on crm_customer.id = A0.customer_id
where crm_customer.deleted is null and crm_customer.id = %(pk)s
group by crm_customer.id limit 1""",
            {"pk": pk},
        )[0]
    except (IndexError, DataError):
        raise ValueError(_("Customer not found"))


def get_customers(search):
    sql = """with self_contact as (
    select c.*, cc.customer_id
    from crm_contact c
    join crm_customercontact cc
    on c.id=cc.contact_id
    where cc.is_basic = true
    and cc.deleted is null
    and c.deleted is null
)
select crm_customer.*, count(A0.id) as forests_count
from crm_customer
join self_contact sc
on sc.customer_id = crm_customer.id
left outer join crm_forestcustomer A0
on crm_customer.id = A0.customer_id
where crm_customer.deleted is null{where_clause}
group by crm_customer.id
"""
    if search:
        where = """
and (concat(sc.name_kanji->>'last_name', '\u3000',
    sc.name_kanji->>'first_name') ilike %(search)s
or concat(sc.name_kana->>'last_name', '\u3000',
    sc.name_kana->>'first_name') ilike %(search)s
or crm_customer.internal_id ilike %(search)s
or sc.email ilike %(search)s
or sc.telephone ilike %(search)s
or sc.mobilephone ilike %(search)s
or concat(sc.postal_code, '\u3000', sc.address->>'sector', '\u3000',
    sc.address->>'municipality', '\u3000', sc.address->>'prefecture') ilike %(search)s)
"""
    else:
        where = ""
    sql = sql.format(where_clause=where)
    return Customer.objects.raw(sql, {"search": "%%%s%%" % search})


def get_customer_contacts(pk: UUID):
    cc_forest_counts = (
        CustomerContact.objects.filter(is_basic=True, contact=OuterRef("pk"))
        .values("customer_id")
        .annotate(forests_count=Count("customer__forestcustomer"))
    )
    cc_is_basic = CustomerContact.objects.filter(is_basic=True, contact=OuterRef("pk"))
    cc_is_basic_business_id = CustomerContact.objects.filter(
        is_basic=True, contact=OuterRef("pk")
    ).annotate(business_id=F("customer__business_id"))
    q = (
        Contact.objects.filter(
            customercontact__customer_id=pk, customercontact__is_basic=False,
        )
        .annotate(
            forest_internal_id=F(
                "customercontact__forestcustomercontact__forestcustomer__forest__internal_id"
            )
        )
        .annotate(
            forest_id=F(
                "customercontact__forestcustomercontact__forestcustomer__forest_id"
            )
        )
        .annotate(
            forestcustomer_id=F(
                "customercontact__forestcustomercontact__forestcustomer_id"
            )
        )
        .annotate(cc_attrs=F("customercontact__attributes"))
        .annotate(forests_count=Subquery(cc_forest_counts.values("forests_count")[:1]))
        .annotate(is_basic=Subquery(cc_is_basic.values("is_basic")[:1]))
        .annotate(customer_id=Subquery(cc_is_basic.values("customer_id")[:1]))
        .annotate(
            business_id=Subquery(cc_is_basic_business_id.values("business_id")[:1])
        )
        .order_by("created_at")
    )
    return q


def get_customer_forests(pk: UUID):
    return (
        Forest.objects.filter(forestcustomer__customer_id=pk)
        .annotate(forestcustomer_id=F("forestcustomer__id"))
        .prefetch_related("forestcustomer_set")
        .order_by("created_at")
    )


def get_list(
    page_num: int = 1,
    per_page: int = 10,
    pre_per_page: Union[int, None] = None,
    order_by: Union[Iterator, None] = None,
    filters: Union[Iterator, None] = None,
):
    if per_page is None:
        offset = None
    else:
        offset = (pre_per_page or per_page) * (page_num - 1)
    if not order_by:
        order_by = []

    fields = [
        "id",
        "internal_id",
        "business_id",
        {"bank_name": RawSQLField("banking->>'bank_name'")},
        {"bank_branch_name": RawSQLField("banking->>'branch_name'")},
        {"bank_account_type": RawSQLField("banking->>'account_type'")},
        {"bank_account_number": RawSQLField("banking->>'account_number'")},
        {"bank_account_name": RawSQLField("banking->>'account_name'")},
        "tags",
        {
            "tags_repr": RawSQLField(
                """
              (select string_agg(tags_repr, ',') tags_repr
              from (
                select concat_ws(':', key, value) as tags_repr
                from jsonb_each_text(tags) as x
              ) as ss)::text
            """
            )
        },
    ]

    query = (
        Query()
        .from_table({"c": Customer}, fields=fields,)
        .join(
            {"self_contact_rel": CustomerContact},
            condition="c.id=self_contact_rel.customer_id and self_contact_rel.is_basic is true",
        )
        .join(
            {"self_contact": Contact},
            condition="self_contact_rel.contact_id=self_contact.id",
            fields=[
                {
                    "fullname_kana": RawSQLField(
                        "concat(self_contact.name_kana->>'last_name', '\u3000', self_contact.name_kana->>'first_name')"
                    )
                },
                {
                    "fullname_kanji": RawSQLField(
                        "concat(self_contact.name_kanji->>'last_name', '\u3000', self_contact.name_kanji->>'first_name')"
                    )
                },
                "mobilephone",
                "telephone",
                "email",
                "postal_code",
                {"sector": "address->>'sector'"},
                {"prefecture": "address->>'prefecture'"},
                {"municipality": "address->>'municipality'"},
            ],
        )
    )
    query = query.wrap()
    if filters:
        query.where(filters)
    total = query.copy().count()

    for order_field in order_by:
        query.order_by(order_field)

    query.limit(per_page, offset)
    return query.select(), total


def create(customer_in: CustomerInputSchema):
    customer = Customer()
    contacts = []
    customer_contacts = []

    self_contact = Contact(**customer_in.basic_contact.dict())
    contacts.append(self_contact)
    contact_rel = CustomerContact(
        customer=customer, contact=self_contact, is_basic=True,
    )
    customer_contacts.append(contact_rel)

    if hasattr(customer_in, "contacts"):
        for data in customer_in.contacts:
            contact = Contact(**data.dict())
            contacts.append(contact)
            contact_rel = CustomerContact(customer=customer, contact=contact)
            customer_contacts.append(contact_rel)
    customer.save()
    Contact.objects.bulk_create(contacts)
    CustomerContact.objects.bulk_create(customer_contacts)
    return customer


def update_basic_info(data):
    customer = data.customer
    self_contact = CustomerContact.objects.get(
        customer_id=customer.id, is_basic=True
    ).contact
    self_contact.name_kanji = data.basic_contact.name_kanji.dict()
    self_contact.name_kana = data.basic_contact.name_kana.dict()
    self_contact.postal_code = data.basic_contact.postal_code
    self_contact.address = data.basic_contact.address.dict()
    self_contact.telephone = data.basic_contact.telephone
    self_contact.mobilephone = data.basic_contact.mobilephone
    self_contact.email = data.basic_contact.email
    self_contact.save()

    # cache saving for customer
    customer.name_kana = self_contact.name_kana
    customer.name_kanji = self_contact.name_kanji
    customer.address = self_contact.address
    customer.save(update_fields=["address", "name_kana", "name_kanji", "updated_at"])

    # cache saving for forest
    values_list = customer.forestcustomer_set.values_list("forest_id", flat=True)
    if len(values_list) > 0:
        async_task(
            refresh_customer_forest_cache,
            list(values_list),
            task_name=f"update_basic_info__forest_cache__{uuid.uuid4().hex.replace('-', '')}",
        )

    return customer


def update_banking(data):
    customer = data.customer
    customer.banking = data.banking
    customer.save(update_fields=["banking", "updated_at"])
    return customer


def contacts_list_with_search(search_str: str = None):
    cc = (
        CustomerContact.objects.filter(is_basic=True, contact=OuterRef("pk"))
        .values("id", "customer_id")
        .annotate(forests_count=Count("customer__forestcustomer"))
    )
    cc_business_id = CustomerContact.objects.filter(
        is_basic=True, contact=OuterRef("pk")
    ).annotate(business_id=F("customer__business_id"))
    queryset = Contact.objects.annotate(
        forests_count=Subquery(cc.values("forests_count")[:1]),
        business_id=Subquery(cc_business_id.values("business_id")[:1]),
    ).all()

    if search_str:
        queryset = queryset.filter(
            Q(name_kanji__first_name__icontains=search_str)
            | Q(name_kanji__last_name__icontains=search_str)
            | Q(name_kana__first_name__icontains=search_str)
            | Q(name_kana__last_name__icontains=search_str)
            | Q(postal_code__icontains=search_str)
            | Q(telephone__icontains=search_str)
            | Q(mobilephone__icontains=search_str)
            | Q(email__icontains=search_str)
            | Q(address__sector__icontains=search_str)
            | Q(address__prefecture__icontains=search_str)
            | Q(address__municipality__icontains=search_str)
        )
    return queryset


def customercontacts_list_with_search(search_str: str = None):
    cc = CustomerContact.objects.filter(is_basic=True, contact=OuterRef("pk"))
    cc_forests_count = cc.values("id", "customer_id").annotate(
        forests_count=Count("customer__forestcustomer")
    )
    queryset = (
        Contact.objects.annotate(
            customer_id=F("customercontact__customer_id"),
            business_id=F("customercontact__customer__business_id"),
            is_basic=F("customercontact__is_basic"),
            forests_count=Subquery(cc_forests_count.values("forests_count")[:1]),
            cc_attrs=F("customercontact__attributes"),
            customer_name_kanji=RawSQL(
                """(select C0.name_kanji
                    from crm_contact C0
                    join crm_customercontact CC0
                        on C0.id = CC0.contact_id and CC0.is_basic = true
                where CC0.customer_id = crm_customercontact.customer_id)""",
                params=[],
            ),
        )
        .filter(is_basic__isnull=False)
        .all()
    )
    if search_str:
        queryset = queryset.filter(
            Q(name_kanji__first_name__icontains=search_str)
            | Q(name_kanji__last_name__icontains=search_str)
            | Q(name_kana__first_name__icontains=search_str)
            | Q(name_kana__last_name__icontains=search_str)
            | Q(postal_code__icontains=search_str)
            | Q(telephone__icontains=search_str)
            | Q(mobilephone__icontains=search_str)
            | Q(email__icontains=search_str)
            | Q(address__sector__icontains=search_str)
            | Q(address__prefecture__icontains=search_str)
            | Q(address__municipality__icontains=search_str)
        )
    return queryset


def delete_customer_contacts(contacts_delete_in: dict):
    customer = contacts_delete_in.customer
    contacts = contacts_delete_in.contacts
    customer_contact = CustomerContact.filter(
        customer_id=customer.pk, contact_id__in=map(lambda c: c.pk, contacts)
    ).delete()
    # should we really delete contact or just relation to customer?
    for contact in contacts:
        try:
            contact.delete()
        except IntegrityError:
            pass
    customer.save(update_fields=["updated_at"])
    return customer


def update_forests(data):
    """
    Assign forests to user, support delete, add forest
    :param data:
    :return:
    """
    customer = data.customer

    # delete relations
    forestcustomers = ForestCustomer.objects.filter(
        forest_id__in=data.deleted, customer_id=customer.pk
    ).all()
    CustomerContact.objects.filter(
        forestcustomercontact__forestcustomer_id__in=forestcustomers.values("id"),
        is_basic=False,
    ).delete()

    for fc in forestcustomers:
        fc.force_delete()

    # assign new relations
    added_forest_customers = []
    for added_forest_pk in data.added:
        forest_customer = ForestCustomer(
            customer_id=customer.id, forest_id=added_forest_pk,
        )
        added_forest_customers.append(forest_customer)

    ForestCustomer.objects.bulk_create(added_forest_customers)
    customer.save(update_fields=["updated_at"])

    customer.refresh_from_db()

    if len(data.added + data.deleted) > 0:
        async_task(
            refresh_customer_forest_cache,
            data.added + data.deleted,
            task_name=f"update_forests__forest_cache__{uuid.uuid4().hex.replace('-', '')}",
        )

    return customer


def update_contacts(contacts_in: ContactsInput):
    customer = contacts_in.customer
    adding = contacts_in.adding
    for contact_data in adding:
        customer_contact, created = CustomerContact.objects.get_or_create(
            customer_id=customer.id, contact_id=contact_data.contact.pk
        )
        if contact_data.forest_id and contacts_in.contact_type == ContactType.forest:
            forestcustomer = next(
                filter(
                    lambda fc: fc.forest_id == contact_data.forest_id,
                    customer.forestcustomer_set.all(),
                )
            )
            ForestCustomerContact.objects.get_or_create(
                forestcustomer=forestcustomer, customercontact=customer_contact
            )
        current_attrs = customer_contact.attributes or {}
        if created:
            customer_contact.attributes = {
                **(current_attrs),
                "contact_type": contacts_in.contact_type,
            }
        if contact_data.relationship_type:
            customer_contact.attributes[
                "relationship_type"
            ] = contact_data.relationship_type.value
        customer_contact.save(update_fields=["attributes", "updated_at"])

    customercontacts = CustomerContact.objects.filter(
        contact_id__in=contacts_in.deleting, customer_id=customer.id,
    ).prefetch_related("contact")
    for cc in customercontacts:
        contact = cc.contact
        if contacts_in.contact_type == ContactType.forest:
            cc.forestcustomercontact_set.all().delete()
            if cc.attributes.get("contact_type") == ContactType.forest:
                cc.force_delete()
        else:
            cc.force_delete()
            contact.force_delete()

    customer.save(update_fields=["updated_at"])
    return customer


def update_banking_info(customer, banking_in):
    has_changed = False
    if customer.banking != banking_in.dict():
        customer.banking = banking_in.dict()
        customer.save(update_fields=["banking", "updated_at"])
        has_changed = True

    return customer, has_changed


def update_customer_memo(customer, memo):
    _memo = customer.attributes.get("memo")
    _updated = False

    if _memo != memo:
        customer.attributes["memo"] = memo
        customer.save()
        _updated = True

    return customer, _updated


def create_contact(customer, contact_in):
    data = contact_in.dict()
    contact_type = data.pop("contact_type")
    contact = Contact(**data)
    contact.save()
    customer_contact = CustomerContact(
        customer_id=customer.id,
        contact_id=contact.id,
        attributes={"contact_type": contact_type.value},
    )
    customer_contact.save()
    customer.save(update_fields=["updated_at"])
    return contact


def get_customer_archives(pk):
    return Archive.objects.filter(archivecustomer__customer_id=pk).order_by(
        "-created_at"
    )


def get_customer_contacts_forests(pk):
    contacts = Contact.objects.filter(
        customercontact__customer_id=pk,
        customercontact__is_basic=False,
        customercontact__attributes__contact_type=ContactType.forest,
    ).values("id")
    customers = Customer.objects.filter(
        customercontact__is_basic=True, customercontact__contact_id__in=contacts
    ).values("id")
    return (
        Forest.objects.filter(forestcustomer__customer_id__in=customers)
        .prefetch_related("forestcustomer_set")
        .order_by("created_at")
    )


def get_customer_by_business_id(busines_id):
    customer = Customer.objects.get(business_id=busines_id)
    if not customer.business_id or len(customer.business_id) == 0:
        raise ValueError(_("Customer ID is empty or not available"))
    return customer


def get_customers_tag_by_ids(ids: list):
    with connection.cursor() as cursor:
        cursor.execute(
            "select distinct jsonb_object_keys(tags) from crm_customer where id in %(ids)s",
            {"ids": tuple(ids)},
        )
        tags = cursor.fetchall()
    return list(itertools.chain(*tags))


def update_customer_tags(data: dict):
    ids = data.get("ids")
    tag_key = data.get("key")
    new_value = data.get("value")
    Customer.objects.filter(id__in=ids, tags__has_key=tag_key).update(
        tags=RawSQL("tags || jsonb_build_object(%s, %s)", params=[tag_key, new_value])
    )


def save_customer_from_csv_data(customer, data):
    self_contact = customer.self_contact
    self_contact.name_kanji = data.name_kanji
    self_contact.name_kana = data.name_kana
    self_contact.postal_code = data.postal_code
    self_contact.address = data.address
    self_contact.telephone = data.telephone
    self_contact.mobilephone = data.mobilephone
    self_contact.email = data.email
    self_contact.save()
    customer.tags = data.tags_json
    customer.banking = data.banking
    customer.save()
