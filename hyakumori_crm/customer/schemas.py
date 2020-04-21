from enum import Enum
from typing import List, Optional, Union

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError as DjValidationError
from django_filters import FilterSet, CharFilter
from pydantic import BaseModel, EmailStr, constr, validator, root_validator
from rest_framework.serializers import ModelSerializer

from ..core.models import HyakumoriDanticModel, HyakumoriDanticUpdateModel, Paginator
from ..crm.common import regexes
from ..crm.common.constants import DEFAULT_EMAIL, EMPTY, UNKNOWN
from ..crm.models import Customer, Forest


class Name(HyakumoriDanticModel):
    last_name: str
    first_name: str


class Address(HyakumoriDanticModel):
    prefecture: Optional[str]
    municipality: Optional[str]
    sector: Optional[str]


class Contact(HyakumoriDanticModel):
    name_kanji: Name
    name_kana: Name
    postal_code: constr(regex=regexes.POSTAL_CODE, strip_whitespace=True)
    address: Optional[Address] = Address
    telephone: Optional[constr(regex=regexes.TELEPHONE_NUMBER, strip_whitespace=True)]
    mobilephone: Optional[
        constr(regex=regexes.MOBILEPHONE_NUMBER, strip_whitespace=True)
    ]
    email: Optional[EmailStr] = DEFAULT_EMAIL


class Banking(HyakumoriDanticModel):
    bank_name: Optional[str] = UNKNOWN
    branch_name: Optional[str] = UNKNOWN
    account_type: Optional[str] = EMPTY
    account_number: Optional[constr(regex=regexes.BANKING_ACCOUNT_NUMBER)]
    account_name: Optional[str] = UNKNOWN


class CustomerStatus(str, Enum):
    registered = "登録済"
    unregistered = "未登録"


class CustomerInputSchema(HyakumoriDanticModel):
    internal_id: Optional[str]
    basic_contact: Contact
    banking: Optional[Banking]


class CustomerRead:
    pass


class CustomerUpdate:
    pass


class CustomerFilter(FilterSet):
    internal_id = CharFilter(lookup_expr="icontains")
    fullname_kanji = CharFilter(lookup_expr="icontains")
    fullname_kana = CharFilter(lookup_expr="icontains")
    postal_code = CharFilter(lookup_expr="icontains")
    address = CharFilter(lookup_expr="icontains")
    telephone = CharFilter(lookup_expr="icontains")
    mobilephone = CharFilter(lookup_expr="icontains")
    prefecture = CharFilter(lookup_expr="icontains")
    municipality = CharFilter(lookup_expr="icontains")
    email = CharFilter(lookup_expr="icontains")
    status = CharFilter(lookup_expr="icontains")
    ranking = CharFilter(lookup_expr="icontains")
    same_name = CharFilter(lookup_expr="icontains")

    class Meta:
        model = Customer
        fields = []


class CustomerPaginator(Paginator):
    @validator("filters")
    def validate_filters(cls, v):
        defined_filters = CustomerFilter.get_filters()
        return {
            field + "__" + defined_filters[field].lookup_expr: value
            for field, value in v.items()
            if field in defined_filters
        }


class ForestSerializer(ModelSerializer):
    class Meta:
        model = Forest
        fields = ["id", "cadastral", "internal_id", "customers_count"]


class CustomerContactsDeleteInput(HyakumoriDanticModel):
    customer: Customer
    contacts: List[Contact]

    class Config:
        arbitrary_types_allowed = True

    @root_validator
    def prepare_contacts(cls, values):
        customer = values.get("customer")
        contacts = values.get("contacts")
        if not customer or not contacts:
            return values
        pks = list(map(lambda c: str(c.pk), contacts))
        if len(set(pks)) < len(pks):
            raise ValueError(_("Duplicate contacts"))
        contact_instances = Contact.objects.filter(
            id__in=pks,
            customercontact__customer_id=customer.id,
            customercontact__is_basic=False,
        )
        db_pks = set(map(lambda c: str(c.pk), contact_instances))
        notfound_pks = set(pks) - set(db_pks)
        if len(notfound_pks) > 0:
            raise ValueError(
                _("Contact {c} not belong to forest and customer").format(
                    c=", ".join(notfound_pks)
                )
            )
        return values

    @validator("contacts", each_item=True, pre=True)
    def check_contact(cls, v):
        if not isinstance(v, Contact):
            try:
                return Contact.objects.get(pk=v)
            except (Contact.DoesNotExist, DjValidationError):
                raise ValueError(_("Contact {pk} not found").format(pk=v))
        return v
