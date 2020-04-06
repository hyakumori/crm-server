from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models

from ...core.models import BaseResourceModel
from ..common.choices import CustomerRegisterStatuses
from ..schemas.customer import Address, Banking
from ..schemas.customer import Contact as ContactSchema
from ..schemas.customer import Name


class DefaultCustomer:
    @staticmethod
    def name():
        return Name().dict()

    @staticmethod
    def address():
        return Address().dict()

    @staticmethod
    def banking():
        return Banking().dict()


class Customer(BaseResourceModel):
    """
    所有者ID    土地所有者名    土地所有者住所	連絡先情報  口座情報	タグ
    """

    name = JSONField(default=DefaultCustomer.name)
    address = JSONField(default=DefaultCustomer.address)
    banking = JSONField(default=DefaultCustomer.banking)
    status = models.CharField(
        max_length=20,
        choices=CustomerRegisterStatuses.choices,
        default=CustomerRegisterStatuses.UNREGISTERED,
    )


class DefaultContact:
    @staticmethod
    def contact_info():
        return ContactSchema().dict()


class Contact(BaseResourceModel):
    contact_info = JSONField(default=DefaultContact.contact_info)
