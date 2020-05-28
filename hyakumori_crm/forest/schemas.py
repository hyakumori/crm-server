from datetime import date
from typing import Optional, List
from uuid import UUID

from django.utils.translation import gettext_lazy as _
from pydantic import validator, root_validator

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
from hyakumori_crm.forest.filters import ForestFilter


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
    if quoted_date_str is None:
        return quoted_date_str
    date_str = quoted_date_str[1:-1]
    if date_str == "":
        return None
    return date_str


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
