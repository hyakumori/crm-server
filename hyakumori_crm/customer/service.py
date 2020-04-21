from typing import Dict, Iterator, Union
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import connection, IntegrityError
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _
from querybuilder.query import Expression, Query

from hyakumori_crm.core.models import RawSQLField
from hyakumori_crm.crm.models import (
    Contact,
    Customer,
    CustomerContact,
    ForestCustomer,
    Forest,
)
from hyakumori_crm.users.models import User

from ..crm.common.constants import CUSTOMER_TAG_KEYS
from .schemas import CustomerInputSchema


def get(pk):
    # try:
    #     return Customer.objects.get(pk=pk)
    # except (Customer.DoesNotExist, ValidationError):
    #     return None
    return None


def get_customer_by_pk(pk):
    try:
        return Customer.objects.get(pk=pk)
    except (Customer.DoesNotExist, ValidationError):
        raise ValueError(_("Customer not found"))


def get_customer_contacts(pk: UUID):
    q = (
        Contact.objects.filter(
            customercontact__customer_id=pk, customercontact__is_basic=False,
        )
        .annotate(
            forest_id=F(
                "customercontact__forestcustomercontact__forestcustomer__forest_id"
            )
        )
        .order_by("created_at")
    )
    return q


def get_customer_forests(pk: UUID):
    return (
        Forest.objects.filter(forestcustomer__customer_id=pk)
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
    admin = User.objects.filter(is_superuser=True, is_active=True).first()
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


def update(customer, data):
    # do update...
    return customer


def contacts_list_with_search(search_str: str = None):
    queryset = Contact.objects.all()
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
