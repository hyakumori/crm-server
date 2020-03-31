from typing import Any
import datetime
from uuid import UUID
from django.db import models
from pydantic import BaseModel, validator


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class InternalMixin(models.Model):
    internal_id = models.CharField(max_length=255, null=True)

    class Meta:
        abstract = True


class HyakumoriDanticModel(BaseModel):
    class Config:
        orm_mode = True
        validate_assignment = True

    @validator("id", pre=True, check_fields=False)
    def get_str_from_uuid(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    @validator("attributes", pre=True, always=True, check_fields=False)
    def validate_attributes(cls, v):
        if v is None:
            return {}
        return v


class HyakumoriDanticUpdateModel(HyakumoriDanticModel):
    context: Any
    updated_at: datetime.datetime

    @validator("updated_at")
    def validate_updated_at(cls, v, values):
        """
        Check if data is newer than the one from database,
        if not, we have to warn the user.
        """
        latest_update = values["context"]["updated_at"]
        if v < latest_update:
            raise ValueError("Some data has changed")
