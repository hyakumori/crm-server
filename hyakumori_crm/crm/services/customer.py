from uuid import uuid4, UUID

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from ..models.customer import Customer, Contact
from ..models.relations import CustomerContact
from ..schemas.customer import CustomerSchema


class CustomerService:
    @staticmethod
    def create_customer(customer: CustomerSchema, author: AbstractUser) -> Customer:
        _customer = Customer()
        _customer.internal_id = customer.internal_id
        _customer.name = customer.name.dict()
        _customer.address = customer.address.dict()
        _customer.banking = customer.banking.dict()
        _customer.status = customer.status.name
        _customer.editor = author
        _customer.author = author
        _customer.save()

        for contact in customer.contacts:
            _contact = Contact()
            _contact.internal_id = uuid4().hex
            _contact.contact_info = contact.dict()
            _contact.author = author
            _contact.editor = author
            _contact.save()

            _customer_contact = CustomerContact()
            _customer_contact.customer = _customer
            _customer_contact.contact = _contact
            _customer_contact.author = author
            _customer_contact.editor = author
            _customer_contact.save()

        return _customer

    @staticmethod
    def delete_customer_by_id(customer_id: UUID):
        customer = Customer.objects.get(pk=customer_id)
        customer.delete()

        for contact_link in customer.customercontact_set.all().iterator():
            contact_link.delete()
            contact_link.contact.delete()

