import datetime
import uuid
from typing import Any, Union, ClassVar, Optional, Sequence, Dict

from behaviors.behaviors import StoreDeleted
from behaviors.managers import StoreDeletedManager
from behaviors.querysets import StoreDeletedQuerySet
from django.db.models import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django_filters import FilterSet
from pydantic import BaseModel, Field, root_validator, validator
from querybuilder.fields import SimpleField

from .permissions import ModelPermissions


class StoreDeletedMixin(StoreDeleted):
    def force_delete(self, *args, **kwargs):
        return models.Model.delete(self, *args, **kwargs)

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDPrimary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class InternalMixin(models.Model):
    internal_id = models.CharField(max_length=255, null=True)

    class Meta:
        abstract = True


class AttributesMixin(models.Model):
    attributes = JSONField(default=dict, encoder=DjangoJSONEncoder)

    class Meta:
        abstract = True


class BaseQuerySet(StoreDeletedQuerySet):
    pass


class BaseRelationModel(
    UUIDPrimary, AttributesMixin, TimestampMixin, StoreDeletedMixin,
):
    objects = StoreDeletedManager.from_queryset(BaseQuerySet)()

    class Meta:
        abstract = True

    def __str__(self):
        return f"Relation ID: {self.id}"


class BaseResourceModel(
    UUIDPrimary, AttributesMixin, InternalMixin, TimestampMixin, StoreDeletedMixin,
):
    REPR_FIELD = "id"
    REPR_NAME = "ID"

    objects = StoreDeletedManager.from_queryset(BaseQuerySet)()

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} - Resource ID: {self.id}, InternalID: {self.internal_id}"

    @classmethod
    def model_perm_cls(cls):
        return type(
            f"{cls.__name__}ModelPermission", (ModelPermissions,), {"model_cls": cls}
        )

    def repr_name(self):
        return self.id


class HyakumoriDanticModel(BaseModel):
    class Config:
        orm_mode = True
        validate_assignment = True
        min_anystr_length = 1
        max_anystr_length = 255
        anystr_strip_whitespace = True
        error_msg_templates = {
            "type_error.none.not_allowed": _("Required"),
            "value_error.str.regex": _("Bad format"),
            "value_error.missing": _("Required"),
            "value_error.email": _("Invalid Email"),
            "value_error.any_str.min_length": _(
                "Required at least {limit_value} character"
            ),
            "value_error.date": _("Invalid date format"),
            "type_error.uuid": _("Invalid UUID"),
            "type_error.enum": _("Invalid value, choices are: {permitted}"),
            "value_error.any_str.max_length": _(
                "ensure this value has at most {limit_value} characters"
            ),
        }

    @validator("*", pre=True)
    def parse_input(cls, v):
        if v == "":
            return None
        return v

    @validator("id", pre=True, check_fields=False)
    def get_str_from_uuid(cls, v):
        if isinstance(v, uuid.UUID):
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
    sort_desc: Sequence[bool] = Field([], alias="sortDesc")
    order_by: Optional[Sequence[str]]
    filters: Optional[Union[Dict[str, Any], FilterSet]]

    MAX_ITEMS: ClassVar = 1000

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

    @validator("filters", pre=True)
    def prepare_filter(cls, v):
        if not v:
            return {}
        return {
            f["criteria"]: f["keyword"]
            for f in v
            if f and f["criteria"] and f["keyword"]
        }

    class Config:
        arbitrary_types_allowed = True


class RawSQLField(SimpleField):
    """
    A field that is created from raw sql string
    """

    def __init__(self, field=None, alias=None, enclose=False):
        """
        Sets the name of the field to the passed in field value

        :param field: A sql expression
        :type field: str

        :param alias: An alias to be used for this field
        :type alias: str

        """
        super().__init__(field, None, alias, None, None)
        self.name = field
        self.enclose = enclose

    def get_select_sql(self):
        if self.enclose:
            return "(%s)" % (self.field)
        return "%s" % (self.field)
