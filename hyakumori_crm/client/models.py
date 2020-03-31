from typing import Optional
import uuid
from django.db import models
from django.contrib.postgres.fields import JSONField
from pydantic import BaseModel, validator

from ..core.models import (
    TimestampMixin,
    InternalMixin,
    HyakumoriDanticModel,
    HyakumoriDanticUpdateModel,
)


class Client(TimestampMixin, InternalMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = JSONField(default=dict)
    attributes = JSONField(default=dict)

    def add_attribute(self, key, value):
        pass


class ClientProfileCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str]
    home_number: Optional[str]
    mobile_number: Optional[str]


class ClientCreate(HyakumoriDanticModel):
    internal_id: Optional[str]
    profile: ClientProfileCreate
    attributes: Optional[dict]


class ClientUpdate(HyakumoriDanticUpdateModel, ClientCreate):
    pass


class ClientRead(HyakumoriDanticModel):
    id: str
    internal_id: Optional[str]
    profile: ClientProfileCreate
    attributes: dict = {}
