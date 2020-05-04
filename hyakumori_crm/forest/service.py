from typing import Iterator, Union

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import F
from django.db.models.expressions import RawSQL

from ..crm.models import (
    Forest,
    ForestCustomer,
    Customer,
    CustomerContact,
    ForestCustomerContact,
    Contact,
)
from .schemas import ForestFilter, CustomerDefaultInput, CustomerContactDefaultInput


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


def get_customers(pk):
    return Customer.objects.raw(
        """select crm_customer.*,
count(A0.id) as forests_count,
crm_forestcustomer.attributes->>'default' as default
from crm_customer
join crm_forestcustomer
on crm_customer.id = crm_forestcustomer.customer_id
left outer join crm_forestcustomer A0
on crm_customer.id = A0.customer_id
where crm_forestcustomer.forest_id = %(pk)s
group by crm_customer.id, crm_forestcustomer.attributes->>'default'""",
        {"pk": pk},
    ).prefetch_related("customercontact_set__contact")


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
