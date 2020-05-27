from datetime import datetime
from typing import Optional, List
from uuid import UUID
from functools import reduce

from django.utils.translation import gettext_lazy as _
from pydantic import validator, root_validator

from pydantic import Field

from ..core.models import HyakumoriDanticModel
from ..crm.models import (
    Archive,
    Contact,
    CustomerContact,
    ArchiveCustomer,
    ArchiveCustomerContact,
)


class ArchiveInput(HyakumoriDanticModel):
    title: str = Field(..., max_length=255)
    content: Optional[str]
    location: Optional[str] = Field(..., max_length=255)
    future_action: Optional[str] = Field(..., max_length=255)
    archive_date: Optional[datetime]


class ArchiveFilter(HyakumoriDanticModel):
    id: str = None
    sys_id: str = None
    archive_date: str = None
    title: str = None
    content: str = None
    author: str = None
    location: str = None
    their_participants: str = None
    our_participants: str = None
    associated_forest: str = None
    tags: str = None

    class Config:
        arbitrary_types_allowed = True
        min_anystr_length = 0


class ArchiveContact(HyakumoriDanticModel):
    contact_id: UUID
    customer_id: Optional[UUID]


class ArchiveCustomerInput(HyakumoriDanticModel):
    archive: Archive
    added: List[ArchiveContact] = []
    deleted: List[ArchiveContact] = []

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def inject_archive(cls, values):
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

        if not values.get("archive"):
            return values
        cls.archive = values["archive"]
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
            ac = cls.archive.archivecustomer_set.get(customer_id=v.customer_id)
        except ArchiveCustomer.DoesNotExist:
            raise ValueError(_("Contact {} not found").format(v.contact_id))
        try:
            ac.archivecustomercontact_set.get(customercontact_id=cc.id)
        except ArchiveCustomerContact.DoesNotExist:
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
            ac = cls.archive.archivecustomer_set.get(customer_id=v.customer_id)
        except ArchiveCustomer.DoesNotExist:
            pass
        else:
            try:
                ac.archivecustomercontact_set.get(customercontact_id=cc.id)
                raise ValueError(_("Contact {} already exists").format(v.contact_id))
            except ArchiveCustomerContact.DoesNotExist:
                pass
        return v
