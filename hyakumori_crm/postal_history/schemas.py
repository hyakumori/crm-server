from datetime import datetime
from typing import Optional, List
from uuid import UUID
from functools import reduce

from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import SerializerMethodField, ModelSerializer
from pydantic import validator, root_validator

from pydantic import Field

from ..core.models import HyakumoriDanticModel
from ..crm.models import (
    PostalHistory,
    CustomerContact,
    PostalHistoryCustomer,
    PostalHistoryCustomerContact,
    Attachment,
)
from ..crm.restful.serializers import AttachmentSerializer
from ..users.serializers import UserSerializer


class PostalHistoryListingSerializer(ModelSerializer):
    author_name = SerializerMethodField(method_name="get_author_name")

    def get_author_name(self, obj: PostalHistory):
        return obj.author.full_name

    class Meta:
        model = PostalHistory
        fields = [
            "id",
            "title",
            "author_name",
            "content",
            "archive_date",
            "attributes",
            "tags",
        ]


class PostalHistorySerializer(ModelSerializer):
    attachments = SerializerMethodField()
    author = UserSerializer()

    class Meta:
        model = PostalHistory
        fields = [
            "id",
            "title",
            "content",
            "archive_date",
            "author",
            "attachments",
            "attributes",
            "tags",
        ]

    def get_attachments(self, obj: PostalHistory):
        try:
            return AttachmentSerializer(
                Attachment.objects.filter(object_id=obj.id), many=True
            ).data
        except Attachment.DoesNotExist:
            return []


class PostalHistoryInput(HyakumoriDanticModel):
    title: str = Field(..., max_length=255)
    content: Optional[str]
    archive_date: Optional[datetime]

    class Config:
        max_anystr_length = None


class PostalHistoryFilter(HyakumoriDanticModel):
    id: str = None
    sys_id: str = None
    archive_date: str = None
    title: str = None
    author: str = None
    content: str = None
    their_participants: str = None
    our_participants: str = None
    associated_forest: str = None
    tags: str = None

    class Config:
        arbitrary_types_allowed = True
        min_anystr_length = 0


class PostalHistoryContact(HyakumoriDanticModel):
    contact_id: UUID
    customer_id: Optional[UUID]


class PostalHistoryCustomerInput(HyakumoriDanticModel):
    postal_history: PostalHistory
    added: List[PostalHistoryContact] = []
    deleted: List[PostalHistoryContact] = []

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def inject_postalhistory(cls, values):
        added = values.get("added")
        if added is not None:
            added_uniq = reduce(lambda l, x: l if x in l else l + [x], added, [])
            if len(added_uniq) < len(added):
                raise ValueError("Some of adding customer-contact pairs are duplicated")

        deleted = values.get("deleted")
        if deleted is not None:
            deleted_uniq = reduce(lambda l, x: l if x in l else l + [x], deleted, [])
            if len(deleted_uniq) < len(deleted):
                raise ValueError(
                    "Some of deleting customer-contact pairs are duplicated"
                )

        if not values.get("postal_history"):
            return values
        cls.postalhistory = values["postal_history"]
        return values

    @validator("deleted", each_item=True)
    def check_deleted(cls, v):
        try:
            if v.customer_id:
                cc = CustomerContact.objects.get(
                    customer_id=v.customer_id, contact_id=v.contact_id
                )
            else:
                cc = CustomerContact.objects.get(is_basic=True, contact_id=v.contact_id)
                v.customer_id = cc.customer_id
        except CustomerContact.DoesNotExist:
            raise ValueError(_("Contact {} not found").format(v.contact_id))
        try:
            ac = cls.postalhistory.postalhistorycustomer_set.get(
                customer_id=v.customer_id
            )
        except PostalHistoryCustomer.DoesNotExist:
            raise ValueError(_("Contact {} not found").format(v.contact_id))
        try:
            ac.postalhistorycustomercontact_set.get(customercontact_id=cc.id)
        except PostalHistoryCustomerContact.DoesNotExist:
            raise ValueError(_("Contact {} not found").format(v.contact_id))
        return v

    @validator("added", each_item=True)
    def check_added(cls, v):
        try:
            if v.customer_id:
                cc = CustomerContact.objects.get(
                    customer_id=v.customer_id, contact_id=v.contact_id
                )
            else:
                cc = CustomerContact.objects.get(is_basic=True, contact_id=v.contact_id)
                v.customer_id = cc.customer_id
        except CustomerContact.DoesNotExist:
            raise ValueError(_("Contact {} not found").format(v.contact_id))
        try:
            ac = cls.postalhistory.postalhistorycustomer_set.get(
                customer_id=v.customer_id
            )
        except PostalHistoryCustomer.DoesNotExist:
            pass
        else:
            try:
                ac.postalhistorycustomercontact_set.get(customercontact_id=cc.id)
                raise ValueError(_("Contact {} already exists").format(v.contact_id))
            except PostalHistoryCustomerContact.DoesNotExist:
                pass
        return v
