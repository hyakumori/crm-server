from typing import Any, List, Sequence, Optional, List, ClassVar
import datetime
from uuid import UUID
from django.db import models
from pydantic import BaseModel, validator, Field, root_validator


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


class Paginator(BaseModel):
    page_num: int = Field(1, alias="page")
    per_page: int = Field(10, alias="itemsPerPage")
    # if user is on page 2, and they want to expand more items
    # we make sure they will be stay in the same offset
    pre_per_page: int = Field(None, alias="preItemsPerPage")
    sort_by: Sequence[str] = Field([], alias="sortBy")
    sort_desc: Sequence[str] = Field([], alias="sortDesc")
    order_by: Optional[Sequence[str]]

    MAX_ITEMS: ClassVar = 100

    @validator("page_num")
    def validate_page_num(cls, page_num):
        if page_num <= 0:
            return 1
        return page_num

    @validator("per_page")
    def validate_per_page(cls, per_page):
        if per_page <= 0:
            return 10
        elif per_page > cls.MAX_ITEMS:
            return cls.MAX_ITEMS
        return per_page

    @validator("pre_per_page")
    def validate_pre_per_page(cls, pre_per_page):
        if pre_per_page is None:
            return pre_per_page
        if pre_per_page <= 0:
            return 10
        elif pre_per_page > cls.MAX_ITEMS:
            return cls.MAX_ITEMS
        return pre_per_page

    @root_validator
    def validate_sort_by(cls, values):
        sort_by = values.get("sort_by")
        sort_desc = values.get("sort_desc")
        if sort_by is None or sort_desc is None:
            return values
        if len(sort_desc) != len(sort_by):
            raise ValueError("sortBy and sortDesc length not match")
        values["order_by"] = map(cls.get_order_by, zip(sort_by, sort_desc))
        return values

    @staticmethod
    def get_order_by(field_pair):
        field = field_pair[0]
        is_desc = field_pair[1]
        if is_desc:
            field = f"-{field}"
        return field
