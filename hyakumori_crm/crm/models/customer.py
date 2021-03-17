from django.db.models import JSONField
from django.db import models
from django.db.models import OuterRef, Subquery, Count, F

from ...core.models import BaseResourceModel, BaseQuerySet, BaseRelationModel
from ...activity.constants import CustomerActions
from ..common.constants import CUSTOMER_ID_PREFIX, CUSTOMER_ID_SEQUENCE
from ..common.utils import generate_sequential_id
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


class CustomerQueryset(BaseQuerySet):
    def basic_contact_id(self):
        cc = CustomerContact.objects.filter(customer=OuterRef("pk")).filter(
            is_basic=True
        )
        return self.annotate(basic_contact_id=Subquery(cc.values("contact_id")[:1]))

    def forests_count(self):
        return self.values("id").annotate(forests_count=Count(F("forestcustomer__id")))


class Customer(BaseResourceModel):
    """
    所有者ID    土地所有者名    土地所有者住所	連絡先情報  口座情報	タグ
    """

    business_id = models.CharField(null=True, max_length=255, db_index=True)
    name_kanji = JSONField(default=DefaultCustomer.name_kanji, db_index=True)
    name_kana = JSONField(default=DefaultCustomer.name_kana, db_index=True)
    address = JSONField(default=DefaultCustomer.address, db_index=True)
    banking = JSONField(default=DefaultCustomer.banking)
    tags = JSONField(default=dict)

    objects = CustomerQueryset.as_manager()

    REPR_FIELD = "business_id"
    REPR_NAME = "顧客ID"

    class Meta:
        permissions = [
            ("manage_customer", "All permissions for customer"),
        ]

    def save(self, *args, **kwargs):
        if not self.business_id or len(self.business_id) == 0:
            self.business_id = generate_sequential_id(
                CUSTOMER_ID_PREFIX, CUSTOMER_ID_SEQUENCE
            )

        super().save(*args, **kwargs)

    @property
    def self_contact(self):
        if not hasattr(self, "_self_contact"):
            try:
                self._self_contact = next(
                    filter(lambda cc: cc.is_basic, self.customercontact_set.all())
                ).contact
            except StopIteration:
                self._self_contact = None
        return self._self_contact

    @property
    def actions(self):
        return CustomerActions

    def repr_name(self):
        return self.business_id


class Contact(BaseResourceModel):
    contact_info = JSONField(default=DefaultContact.contact_info)
    name_kanji = JSONField(default=DefaultCustomer.name_kanji, db_index=True)
    name_kana = JSONField(default=DefaultCustomer.name_kana, db_index=True)
    address = JSONField(default=DefaultCustomer.address, db_index=True)
    postal_code = models.CharField(default=None, max_length=200, null=True)
    telephone = models.CharField(default=None, max_length=200, null=True)
    mobilephone = models.CharField(default=None, max_length=200, null=True)
    email = models.EmailField(default=None, max_length=200, null=True)

    class Meta:
        permissions = [
            ("manage_contact", "All permissions for contact"),
        ]


class CustomerContact(BaseRelationModel):
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
    contact = models.ForeignKey("Contact", on_delete=models.PROTECT)
    is_basic = models.BooleanField(
        default=False
    )  # if True, will show in the list of Owners for select direct owners

    class Meta:
        permissions = [
            ("manage_customercontact", "All permissions for customer contact"),
        ]

    @property
    def is_default(self):
        return self.attributes["is_default"]

    @property
    def relative_type(self):
        if "relative_type" in self.attributes:
            return None

        return self.attributes["relative_type"]

    def set_relative_type(self, value):
        self.attributes["relative_type"] = value
        return self


class ForestCustomer(BaseRelationModel):
    forest = models.ForeignKey("Forest", on_delete=models.PROTECT)
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ("manage_forestcustomer", "All permissions for forest customer"),
        ]


class ForestCustomerContact(BaseRelationModel):
    forestcustomer = models.ForeignKey("ForestCustomer", on_delete=models.CASCADE)
    customercontact = models.ForeignKey("CustomerContact", on_delete=models.CASCADE)
