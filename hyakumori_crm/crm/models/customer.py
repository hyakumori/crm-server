from django.contrib.postgres.fields.jsonb import JSONField

from ...core.models import BaseResourceModel
from ..schemas.customer import Address, Banking
from ..schemas.customer import Contact as ContactSchema
from ..schemas.customer import Name


class DefaultCustomer:
    @staticmethod
    def name_kanji():
        return Name().dict()

    @staticmethod
    def name_kana():
        return Name().dict()

    @staticmethod
    def address():
        return Address().dict()

    @staticmethod
    def banking():
        return Banking().dict()


class DefaultContact:
    @staticmethod
    def contact_info():
        return ContactSchema().dict()


class Customer(BaseResourceModel):
    """
    所有者ID    土地所有者名    土地所有者住所	連絡先情報  口座情報	タグ
    """

    name_kanji = JSONField(default=DefaultCustomer.name_kanji, db_index=True)
    name_kana = JSONField(default=DefaultCustomer.name_kana, db_index=True)
    address = JSONField(default=DefaultCustomer.address, db_index=True)
    banking = JSONField(default=DefaultCustomer.banking)
    tags = JSONField(default=list)


class Contact(BaseResourceModel):
    contact_info = JSONField(default=DefaultContact.contact_info)
