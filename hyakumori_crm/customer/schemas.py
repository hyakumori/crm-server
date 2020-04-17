from enum import Enum
from typing import List, Optional, Union

from django_filters import FilterSet, CharFilter
from pydantic import BaseModel, EmailStr, constr, validator
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
