from django.db import models
from django.contrib.postgres.fields import JSONField
from ..core.models import (
    TimestampMixin,
    InternalMixin,
    HyakumoriDanticModel,
    HyakumoriDanticUpdateModel,
)
from pydantic import BaseModel
from typing import Optional
import uuid

class Forest(TimestampMixin, InternalMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attributes = JSONField(default=dict)
    basic_info = JSONField(default=dict)
    geo_data = JSONField(default=dict)

    def add_attribute(self, key, value):
        pass

class CreateGeoData(BaseModel):
    latitude: float
    longitude: float
    address: str

class CreateBasicInfo(BaseModel):
    acreage: str
    status: Optional[str]

class CreateForest(HyakumoriDanticModel):
    internal_id: Optional[str]
    geo_data: CreateGeoData
    basic_info: CreateBasicInfo
    attributes: Optional[dict]
