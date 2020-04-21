from typing import Iterator, Union

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import connections
from django.db.utils import OperationalError

from ..crm.models import (
    Forest,
    ForestCustomer,
    Customer,
    CustomerContact,
    ForestCustomerContact,
)
from .schemas import ForestFilter


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
    forests = query.order_by(*order_by)[offset : offset + per_page]
    return forests, total


def update(forest: Forest, forest_in: dict):
    forest.cadastral = forest_in["cadastral"]
    forest.contracts = forest_in["contracts"]
    forest.save()
    return forest


def update_owners(owner_pks_in):
    forest = owner_pks_in.forest
    ForestCustomer.objects.filter(
        customer_id__in=owner_pks_in.deleted, forest_id=forest.pk
    ).delete()
    added_forest_customers = []
    for added_owner_pk in owner_pks_in.added:
        forest_customer = ForestCustomer(
            customer_id=added_owner_pk, forest_id=forest.pk,
        )
        added_forest_customers.append(forest_customer)
    ForestCustomer.objects.bulk_create(added_forest_customers)
    forest.save(update_fields=["updated_at"])
    return forest


def set_forest_owner_contacts(forest: Forest, forest_owner_contact_in: dict):
    customer = forest_owner_contact_in.customer
    contacts = forest_owner_contact_in.contacts
    forestcustomer = customer.forestcustomer_set.get(forest_id=forest.pk)
    for contact in contacts:
        customer_contact, _ = CustomerContact.objects.get_or_create(
            customer_id=customer.id, contact_id=contact.contact.pk
        )
        if contact.set_forest:
            ForestCustomerContact.objects.get_or_create(
                forestcustomer=forestcustomer, customercontact=customer_contact
            )
        customer_contact.attributes = {
            **(customer_contact.attributes or {}),
            "relationship_type": contact.relationship_type,
        }
        customer_contact.save(update_fields=["attributes", "updated_at"])
    customer.save(update_fields=["updated_at"])
    forest.save(update_fields=["updated_at"])
    return forest
