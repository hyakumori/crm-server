from uuid import UUID
from django.db import models
from pydantic import BaseModel, validator


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class InternalMixin(models.Model):
    internal_id = models.CharField(max_length=255)

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
