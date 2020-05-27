import operator
from datetime import date
from functools import reduce
from typing import Optional, List
from uuid import UUID

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_filters import FilterSet, CharFilter, DateFilter
from pydantic import validator, root_validator
from pydantic.dataclasses import dataclass

from hyakumori_crm.core.models import HyakumoriDanticModel, Paginator
from hyakumori_crm.crm.models import (
    Forest,
    ForestCustomer,
    Customer,
    CustomerContact,
    ForestCustomerContact,
)
from hyakumori_crm.crm.schemas.contract import ContractType
from hyakumori_crm.crm.schemas.forest import LandAttribute, ForestAttribute
from hyakumori_crm.crm.common.utils import tags_csv_to_dict


class ForestFilter(FilterSet):
    internal_id = CharFilter(method="icontains_filter")
    cadastral__prefecture = CharFilter(method="icontains_filter")
    cadastral__municipality = CharFilter(method="icontains_filter")
    cadastral__sector = CharFilter(method="icontains_filter")
    cadastral__subsector = CharFilter(method="icontains_filter")
    owner__name_kana = CharFilter(method="owner_icontains_filter")
    owner__name_kanji = CharFilter(method="owner_icontains_filter")
    contracts__0__status = CharFilter(method="icontains_filter")
    contracts__0__start_date = DateFilter(method="exact_date_filter")
    contracts__0__end_date = DateFilter(method="exact_date_filter")
    contracts__1__status = CharFilter(method="icontains_filter")
    contracts__1__start_date = DateFilter(method="exact_date_filter")
    contracts__1__end_date = DateFilter(method="exact_date_filter")
    contracts__2__status = CharFilter(method="icontains_filter")
    contracts__2__start_date = DateFilter(method="exact_date_filter")
    contracts__2__end_date = DateFilter(method="exact_date_filter")
    tag__danchi = CharFilter(method="icontains_filter")
    tag__manage_type = CharFilter(method="icontains_filter")

    def icontains_filter(self, queryset, name, value):
        return queryset.filter(**{name + "__icontains": value})

    def owner_icontains_filter(self, queryset, name, value):
        search_field = ""
        if name.find("name_kana") >= 0:
            search_field = f"attributes__customer_cache__repr_name_kana"
        if name.find("name_kanji") >= 0:
            search_field = f"attributes__customer_cache__repr_name_kanji"

        search_field_filter = search_field + "__icontains"
        values = value.split(" ")
        qs = queryset.filter(
            reduce(
                operator.and_, (Q(**{search_field_filter: value}) for value in values)
            )
        )
        return qs

    def exact_date_filter(self, queryset, name, value):
        return queryset.filter(**{name: value})

    class Meta:
        model = Forest
        fields = []


class ForestPaginator(Paginator):
    @validator("filters")
    def validate_filters(cls, filter_input):
        return ForestFilter(filter_input)


class Cadastral(HyakumoriDanticModel):
    prefecture: str
    municipality: str
    sector: str
    subsector: Optional[str]


class Contract(HyakumoriDanticModel):
    type: ContractType
    status: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]


class ForestInput(HyakumoriDanticModel):
    forest: Forest
    cadastral: Cadastral
    contracts: List[Contract]

    class Config:
        arbitrary_types_allowed = True


class OwnerPksInput(HyakumoriDanticModel):
    forest: Forest
    added: List[UUID] = []
    deleted: List[UUID] = []

    class Config:
        arbitrary_types_allowed = True

    @validator("deleted")
    def check_deleted(cls, v):
        owner_pks = ForestCustomer.objects.filter(customer_id__in=v).values_list(
            "customer_id", flat=True
        )
        invalid_pks = set(v) - set(owner_pks)
        if len(invalid_pks) > 0:
            raise ValueError(
                _("Customer Id {} not found").format(", ".join(invalid_pks))
            )
        return v

    @validator("added")
    def check_added(cls, v):
        owner_pks = Customer.objects.filter(id__in=v).values_list("id", flat=True)
        invalid_pks = set(v) - set(owner_pks)
        if len(invalid_pks) > 0:
            raise ValueError(
                _("Customer Id {} not found").format(", ".join(invalid_pks))
            )
        return v


class CustomerDefaultInput(HyakumoriDanticModel):
    forest: Forest
    customer_id: UUID
    default: bool

    class Config:
        arbitrary_types_allowed = True

    @root_validator
    def validate_customer_id(cls, values):
        forest = values.get("forest")
        customer_id = values.get("customer_id")
        if not forest or not customer_id:
            return values
        try:
            ForestCustomer.objects.get(forest_id=forest.id, customer_id=customer_id)
        except ForestCustomer.DoesNotExist:
            raise ValueError(_("Customer {v} not found").format(v=customer_id))
        return values


class CustomerContactDefaultInput(HyakumoriDanticModel):
    forest: Forest
    customer_id: UUID
    contact_id: UUID
    default: bool

    class Config:
        arbitrary_types_allowed = True

    @root_validator
    def validate(cls, values):
        forest = values.get("forest")
        customer_id = values.get("customer_id")
        contact_id = values.get("contact_id")
        if not forest or not customer_id or not contact_id:
            return values
        try:
            fc = ForestCustomer.objects.get(
                forest_id=forest.id, customer_id=customer_id
            )
        except ForestCustomer.DoesNotExist:
            raise ValueError(_("Customer {v} not found").format(v=customer_id))
        try:
            cc = CustomerContact.objects.get(
                customer_id=customer_id, contact_id=contact_id
            )
            fcc = ForestCustomerContact.objects.get(
                forestcustomer_id=fc.id, customercontact_id=cc.id
            )
        except (CustomerContact.DoesNotExist, ForestCustomerContact.DoesNotExist):
            raise ValueError(_("Contact {v} not found").format(v=customer_id))

        return values


class ForestMemoInput(HyakumoriDanticModel):
    forest: Forest
    memo: str

    class Config:
        arbitrary_types_allowed = True
        min_anystr_length = 0


def csv_contract_date_normalize(quoted_date_str):
    return quoted_date_str[1:-1]


class CsvContract(Contract):
    _normalize_start_date = validator("start_date", allow_reuse=True, pre=True)(
        csv_contract_date_normalize
    )
    _normalize_end_date = validator("end_date", allow_reuse=True, pre=True)(
        csv_contract_date_normalize
    )


class ForestCsvInput(HyakumoriDanticModel):
    id: Optional[UUID]
    internal_id: str
    cadastral: Cadastral
    contracts: List[CsvContract]
    land_attributes: List[LandAttribute]
    forest_attributes: List[ForestAttribute]
    tags: Optional[str]

    class CsvConfig:
        arbitrary_types_allowed = True

    @validator("tags")
    def tags_validator(cls, value):
        try:
            tags_csv_to_dict(value)
        except ValueError:
            raise ValueError(_("Invalid format (tag1:value1; tag2:value2)"))
        return value

    @property
    def tags_json(self):
        return tags_csv_to_dict(self.tags)
