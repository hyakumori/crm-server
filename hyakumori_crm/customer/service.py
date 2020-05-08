import logging
from typing import Iterator, Union
from uuid import UUID

from django.db import DataError, IntegrityError, connection
from django.db.models import Count, F, OuterRef, Q, Subquery
from django.db.models.expressions import RawSQL
from django.utils.translation import gettext_lazy as _
from querybuilder.query import Expression, Query

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
from .schemas import ContactType, CustomerInputSchema
from ..crm.common.constants import CUSTOMER_TAG_KEYS


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
and (concat(sc.name_kanji->>'last_name', ' ',
    sc.name_kanji->>'first_name') ilike %(search)s
or concat(sc.name_kana->>'last_name', ' ',
    sc.name_kana->>'first_name') ilike %(search)s
or crm_customer.internal_id ilike %(search)s
or sc.email ilike %(search)s
or sc.telephone ilike %(search)s
or sc.mobilephone ilike %(search)s
or concat(sc.postal_code, ' ', sc.address->>'sector', ' ',
    sc.address->>'municipality', ' ', sc.address->>'prefecture') ilike %(search)s)
"""
    else:
        where = ""
    sql = sql.format(where_clause=where)
    return Customer.objects.raw(sql, {"search": "%%%s%%" % search})


def get_customer_contacts(pk: UUID):
    cc = (
        CustomerContact.objects.filter(is_basic=True, contact=OuterRef("pk"))
        .values("id", "customer_id")
        .annotate(forests_count=Count("customer__forestcustomer"))
    )
    q = (
        Contact.objects.filter(
            customercontact__customer_id=pk, customercontact__is_basic=False,
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
        .annotate(forests_count=Subquery(cc.values("forests_count")[:1]))
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


def get_customer_tags_keys():
    with connection.cursor() as c:
        raw_query = "select distinct (jsonb_object_keys(tags)) from crm_customer"
        c.execute(raw_query)
        result = [row[0] for row in c.fetchall()]
        return result


def get_tag_fields_for_query():
    tags_keys = get_customer_tags_keys()
    # only mapping keys available in DB
    tags = [(k, v) for k, v in CUSTOMER_TAG_KEYS.items() if v in tags_keys]
    tags_fields = [{tag[0]: f"tags->>'{tag[1]}'"} for tag in tags]
    return tags_fields


def get_list(
    page_num: int = 1,
    per_page: int = 10,
    pre_per_page: Union[int, None] = None,
    order_by: Union[Iterator, None] = None,
    filters: Union[dict, None] = None,
):
    offset = (pre_per_page or per_page) * (page_num - 1)
    if not order_by:
        order_by = []

    representatives = (
        Query()
        .from_table(
            {"contact": Contact},
            [
                {
                    "fullname_kana": RawSQLField(
                        "concat(contact.name_kana->>'last_name', ' ', contact.name_kana->>'first_name')"
                    )
                }
            ],
        )
        .join(
            {"contact_rel": CustomerContact},
            condition="contact.id = contact_rel.contact_id",
        )
        .where(Q(customer_id=Expression("c.id")))
        .where(~Q(is_basic=Expression("true")))
        .order_by(
            "attributes->>'default'", table="contact_rel", desc=True, nulls_last=True
        )
        .limit(1)
    )

    tags_fields = get_tag_fields_for_query()

    fields = [
        "id",
        "internal_id",
        {"representative": RawSQLField(representatives.get_sql(), enclose=True)},
    ]

    fields += tags_fields

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
                        "concat(self_contact.name_kana->>'last_name', ' ', self_contact.name_kana->>'first_name')"
                    )
                },
                {
                    "fullname_kanji": RawSQLField(
                        "concat(self_contact.name_kanji->>'last_name', ' ', self_contact.name_kanji->>'first_name')"
                    )
                },
                "mobilephone",
                "telephone",
                "email",
                "postal_code",
                {"address": "address->>'sector'"},
                {"prefecture": "address->>'prefecture'"},
                {"municipality": "address->>'municipality'"},
            ],
        )
    )
    query = query.wrap()
    if filters:
        query.where(**filters)
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
    for forestcustomer in customer.forestcustomer_set.iterator():
        try:
            forest = forestcustomer.forest
            forest.owner["address"] = self_contact.address
            forest.save(update_fields=["owner", "updated_at"])
        except:
            logging.warning(
                f"could not saving latest user address in forest: {forestcustomer.forest.pk}"
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
    queryset = Contact.objects.annotate(
        forests_count=Subquery(cc.values("forests_count")[:1])
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
    queryset = Contact.objects.annotate(
        customer_id=F("customercontact__customer_id"),
        is_basic=F("customercontact__is_basic"),
        customer_name_kanji=RawSQL(
            """(select C0.name_kanji
from crm_contact C0
join crm_customercontact CC0
on C0.id = CC0.contact_id and CC0.is_basic = true
where CC0.customer_id = crm_customercontact.customer_id)""",
            params=[],
        ),
    ).all()
    if search_str:
        queryset = queryset.filter(
            Q(name_kanji__first_name__icontains=search_str)
            | Q(id__icontains=search_str)
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
    customer = data.customer
    for fc in ForestCustomer.objects.filter(
        forest_id__in=data.deleted, customer_id=customer.pk
    ).all():
        fc.force_delete()
    added_forest_customers = []
    for added_forest_pk in data.added:
        forest_customer = ForestCustomer(
            customer_id=customer.id, forest_id=added_forest_pk,
        )
        added_forest_customers.append(forest_customer)
    ForestCustomer.objects.bulk_create(added_forest_customers)
    customer.save(update_fields=["updated_at"])
    return customer


def update_contacts(contacts_in: dict):
    customer = contacts_in.customer
    adding = contacts_in.adding
    CustomerContact.objects.filter(
        contact_id__in=contacts_in.deleting, customer_id=customer.id
    ).delete()
    for contact_data in adding:
        customer_contact, _ = CustomerContact.objects.get_or_create(
            customer_id=customer.id, contact_id=contact_data.contact.pk
        )
        if contact_data.forest_id:
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
        customer_contact.attributes = {
            **(current_attrs),
            "contact_type": ContactType.forest.value
            if contact_data.forest_id
            else contact_data.contact_type.value,
        }
        if contact_data.relationship_type:
            customer_contact.attributes[
                "relationship_type"
            ] = contact_data.relationship_type.value
        customer_contact.save(update_fields=["attributes", "updated_at"])
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
