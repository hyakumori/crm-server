from typing import Iterator, Union

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connections
from django.db.utils import OperationalError

from ..crm.models import Forest, ForestCustomer, Customer, CustomerContact
from .schemas import ForestFilter


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


def update_owners(forest: Forest, owner_pks_in: dict):
    ForestCustomer.objects.filter(
        customer_id__in=owner_pks_in["deleted"], forest_id=forest.pk
    ).delete()
    added_forest_customers = []
    customers = (
        Customer.objects.basic_contact_id()
        .filter(pk__in=owner_pks_in["added"])
        .values_list("id", "basic_contact_id")
    )
    customers_map = {c[0]: c[1] for c in customers}
    for added_owner_pk in owner_pks_in["added"]:
        forest_customer = ForestCustomer(
            customer_id=added_owner_pk,
            forest_id=forest.pk,
            contact_id=customers_map[added_owner_pk],
        )
        added_forest_customers.append(forest_customer)
    ForestCustomer.objects.bulk_create(added_forest_customers)
    forest.save(update_fields=["updated_at"])
    return forest


def set_forest_owner_contact(forest: Forest, forest_owner_contact_in: dict):
    customer = forest_owner_contact_in.customer
    contact = forest_owner_contact_in.contact
    CustomerContact.objects.get_or_create(
        customer_id=customer.id, contact_id=contact.id,
    )
    forest_customer = ForestCustomer.objects.get(
        forest_id=forest.id, customer_id=customer.id,
    )
    forest_customer.contact_id = contact.id
    forest_customer.save(update_fields=["contact_id", "updated_at"])
    customer.save(update_fields=["updated_at"])
    forest.save(update_fields=["updated_at"])
    return forest
