from typing import Union
from uuid import UUID

from django.db import transaction
from django.db.models import Q
from hyakumori_crm.crm.models.customer import Customer
from hyakumori_crm.crm.models.forest import Forest
from hyakumori_crm.crm.models.relations import ForestCustomer, ForestCustomerContact
from hyakumori_crm.crm.schemas.forest import ForestSchema

from ..lib.utils import key_value_to_dict
from .customer import CustomerService


class ForestService:
    @staticmethod
    def create_forest(forest: ForestSchema) -> Forest:
        _forest = Forest()
        _forest.internal_id = forest.internal_id
        _forest.cadastral = forest.cadastral.dict()
        _forest.owner = forest.original_owner.dict()
        _forest.tag = forest.tag.dict()
        _forest.contracts = [contract.dict() for contract in forest.contracts]
        _forest.land_attributes = key_value_to_dict(forest.land_attributes)
        _forest.forest_attributes = key_value_to_dict(forest.forest_attributes)
        _forest.save()

        return _forest

    @staticmethod
    def create_forest_customer_relation(
        forest_id: Union[str, UUID], customer_id: UUID, forest_internal=False,
    ):
        customer = Customer.objects.get(pk=customer_id)
        if forest_internal:
            forest = Forest.objects.get(internal_id=forest_id)
        else:
            forest = Forest.objects.get(pk=forest_id)

        contact, customercontact = CustomerService.get_basic_contact(customer_id)
        link_existed = ForestCustomer.objects.filter(
            Q(customer=customer) & Q(forest=forest)
        ).first()

        if link_existed:
            print("Link exist, skipped")
            return link_existed

        relation = ForestCustomer()
        relation.forest = forest
        relation.customer = customer
        relation.contact = contact
        relation.save()

        relation_contact = ForestCustomerContact()
        relation_contact.forestcustomer = relation
        relation_contact.customercontact = customercontact
        relation_contact.save()

        return relation

    @staticmethod
    def mark_related_count(
        forest_id: Union[str, UUID], related_count: int, forest_internal=False
    ):
        if forest_internal:
            forest = Forest.objects.get(internal_id=forest_id)
        else:
            forest = Forest.objects.get(pk=forest_id)
        forest.attributes["original_related_count"] = related_count
        forest.save()
