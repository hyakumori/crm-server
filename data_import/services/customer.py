from uuid import UUID, uuid4

from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from hyakumori_crm.crm.models.customer import Contact, Customer
from hyakumori_crm.crm.models.relations import CustomerContact
from hyakumori_crm.crm.schemas.customer import CustomerSchema
from hyakumori_crm.crm.schemas.forest import ForestOwner


class CustomerService:
    @staticmethod
    def create_customer(customer: CustomerSchema, author: AbstractUser, link_contact: Contact = None, is_basic=True) -> Customer:
        _customer = Customer()
        _customer.internal_id = customer.internal_id
        _customer.name_kanji = customer.name_kanji.dict()
        _customer.name_kana = customer.name_kana.dict()
        _customer.address = customer.address.dict()
        _customer.banking = customer.banking.dict()
        _customer.tags = customer.tags
        _customer.editor = author
        _customer.author = author
        _customer.save()

        if link_contact is None:
            _contact = Contact()
            _contact.internal_id = uuid4().hex
            _contact.contact_info = customer.basic_contact.dict()
            _contact.name_kanji = customer.basic_contact.name_kanji.dict()
            _contact.name_kana = customer.basic_contact.name_kana.dict()
            _contact.address = customer.basic_contact.address.dict()
            _contact.postal_code = customer.basic_contact.postal_code
            _contact.telephone = customer.basic_contact.telephone
            _contact.mobilephone = customer.basic_contact.mobilephone
            _contact.email = customer.basic_contact.email
            _contact.editor = author
            _contact.author = author
            _contact.save()
        else:
            _contact = link_contact

        _customer_contact = CustomerContact()
        _customer_contact.customer = _customer
        _customer_contact.contact = _contact
        _customer_contact.is_basic = is_basic
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

    @staticmethod
    def get_basic_contact(customer_id) -> Contact:
        customer_contact_link = CustomerContact.objects.filter(Q(is_basic=True) & Q(customer_id=customer_id)).first()
        contact = customer_contact_link.contact
        return contact

    @staticmethod
    def has_owner(owner: ForestOwner) -> bool:
        # check forest.owner in forest or not
        _customer = Customer.objects.filter(
            Q(name_kanji__first_name=owner.name_kanji.first_name)
            & Q(name_kanji__last_name=owner.name_kanji.last_name)
            & Q(address__prefecture=owner.address.prefecture)
            & Q(address__municipality=owner.address.municipality)
            & Q(address__sector=owner.address.sector)
        ).first()

        return _customer
