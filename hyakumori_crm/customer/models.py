from typing import Optional, List
import uuid
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel, validator

from ..core.models import (
    TimestampMixin,
    InternalMixin,
    HyakumoriDanticModel,
    HyakumoriDanticUpdateModel,
)


class Customer(TimestampMixin, InternalMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = JSONField(default=dict)
    attributes = JSONField(default=dict)
    contacts = models.ManyToManyField(through="CustomerContact", to="Contact")

    def add_attribute(self, key, value):
        pass

    def __repr__(self):
        return self.profile["last_name"] + " " + self.profile["first_name"]


class Contact(TimestampMixin, InternalMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = JSONField(default=dict)

    def __repr__(self):
        return self.profile["last_name"] + " " + self.profile["first_name"]


class RELATIONSHIP_TYPE(models.TextChoices):
    SON = "SON", _("Son")
    DAUGHTER = "DAUGHTER", _("Daughter")
    WIFE = "WIFE", _("Wife")
    HUSBAND = "HUSBAND", _("Husband")
    GRANDSON = "GRANDSON", _("Grandson")
    GRANDDAUGHTER = "GRANDDAUGHTER", _("Granddaughter")
    SISTER = "SISTER", _("Sister")
    BROTHER = "BROTHER", _("Brother")


class CustomerContact(TimestampMixin, models.Model):
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
    contact = models.ForeignKey("Contact", on_delete=models.CASCADE)
    attributes = JSONField(default=dict)
    relationship_type = models.CharField(
        max_length=20, choices=RELATIONSHIP_TYPE.choices
    )
    default = models.BooleanField(default=False)


class CustomerProfileCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str]
    home_number: Optional[str]
    mobile_number: Optional[str]


class ContactCreate(BaseModel):
    internal_id: Optional[str]
    profile: CustomerProfileCreate
    relationship_type: RELATIONSHIP_TYPE
    default: Optional[bool]


class CustomerCreate(HyakumoriDanticModel):
    internal_id: Optional[str]
    profile: CustomerProfileCreate
    attributes: Optional[dict]
    contacts: Optional[List[ContactCreate]]


class CustomerUpdate(HyakumoriDanticUpdateModel, CustomerCreate):
    pass


class CustomerRead(HyakumoriDanticModel):
    id: str
    internal_id: Optional[str]
    profile: CustomerProfileCreate
    attributes: dict = {}
