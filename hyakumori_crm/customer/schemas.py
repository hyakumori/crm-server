from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError as DjValidationError
from django_filters import FilterSet, CharFilter
from rest_framework.serializers import ModelSerializer
from pydantic import BaseModel, EmailStr, constr, validator, root_validator
from pydantic.error_wrappers import ValidationError
from pydantic.errors import MissingError

from ..core.models import HyakumoriDanticModel, HyakumoriDanticUpdateModel, Paginator
from ..crm.common import regexes
from ..crm.common.constants import DEFAULT_EMAIL, EMPTY, UNKNOWN
from ..crm.models import Customer, Forest, ForestCustomer, Contact


class Name(HyakumoriDanticModel):
    last_name: str
    first_name: str


class Address(HyakumoriDanticModel):
    prefecture: Optional[str]
    municipality: Optional[str]
    sector: Optional[str]


class ContactInput(HyakumoriDanticModel):
    name_kanji: Name
    name_kana: Name
    postal_code: constr(regex=regexes.POSTAL_CODE, strip_whitespace=True)
    address: Optional[Address] = {}
    telephone: Optional[constr(regex=regexes.TELEPHONE_NUMBER, strip_whitespace=True)]
    mobilephone: Optional[
        constr(regex=regexes.MOBILEPHONE_NUMBER, strip_whitespace=True)
    ]
    email: Optional[EmailStr] = DEFAULT_EMAIL


class BankingInput(HyakumoriDanticModel):
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
    basic_contact: ContactInput


class CustomerUpdateSchema(CustomerInputSchema):
    customer: Customer

    class Config:
        arbitrary_types_allowed = True


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


class ForestPksInput(HyakumoriDanticModel):
    customer: Customer
    added: List[UUID] = []
    deleted: List[UUID] = []

    class Config:
        arbitrary_types_allowed = True

    @validator("deleted")
    def check_deleted(cls, v):
        forest_pks = ForestCustomer.objects.filter(forest_id__in=v).values_list(
            "forest_id", flat=True
        )
        invalid_pks = set(v) - set(forest_pks)
        if len(invalid_pks) > 0:
            raise ValueError(_("Forest Id {} not found").format(", ".join(invalid_pks)))
        return v

    @validator("added")
    def check_added(cls, v):
        forest_pks = Forest.objects.filter(id__in=v).values_list("id", flat=True)
        invalid_pks = set(v) - set(forest_pks)
        if len(invalid_pks) > 0:
            raise ValueError(_("Forest Id {} not found").format(", ".join(invalid_pks)))
        return v


class RelationshipType(str, Enum):
    self = "本人"
    parents = "両親"
    husband = "夫"
    wife = "妻"
    son = "息子"
    daughter = "娘"
    grandchild = "孫"
    friend = "友人"
    relative = "その他親族"
    other = "その他"


class ContactType(str, Enum):
    forest = "FOREST"
    family = "FAMILY"
    others = "OTHERS"


class SingleSelectContactInput(HyakumoriDanticModel):
    contact: Contact
    relationship_type: Optional[RelationshipType]
    forest_id: Optional[UUID]
    contact_type: ContactType

    class Config:
        arbitrary_types_allowed = True

    @validator("contact", pre=True)
    def prepare_contact(cls, v):
        if not isinstance(v, Contact):
            try:
                return Contact.objects.get(pk=v)
            except (Contact.DoesNotExist, DjValidationError):
                raise ValueError(_("Contact {} not found").format(v))
        return v


class ContactsInput(HyakumoriDanticModel):
    customer: Customer
    adding: List[SingleSelectContactInput] = []
    deleting: List[UUID] = []

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def preparing(cls, values):
        customer = values.get("customer")
        cls.customer_forest_pks = customer.forestcustomer_set.all().values_list(
            "forest_id", flat=True
        )
        cls.customer_contact_pks = customer.customercontact_set.all().values_list(
            "contact_id", flat=True
        )
        return values

    @validator("adding", each_item=True)
    def validate_adding_forest_ids(cls, v):
        if v.forest_id and v.forest_id not in cls.customer_forest_pks:
            raise ValueError(_("Forest {} not found").format(v.forest_id))
        return v

    @validator("deleting", each_item=True)
    def validate_deleting_contact_ids(cls, v):
        if v not in cls.customer_contact_pks:
            raise ValueError(_("Contact {} not found").format(v))
        return v


class CustomerMemoInput(HyakumoriDanticModel):
    customer: Customer
    memo: str

    class Config:
        arbitrary_types_allowed = True


class RequiredAddress(HyakumoriDanticModel):
    prefecture: Optional[str]
    municipality: Optional[str]
    sector: str


class RequiredContactInput(HyakumoriDanticModel):
    name_kanji: Name
    name_kana: Name
    postal_code: Optional[constr(regex=regexes.POSTAL_CODE, strip_whitespace=True)]

    address: RequiredAddress
    telephone: Optional[constr(regex=regexes.TELEPHONE_NUMBER, strip_whitespace=True)]

    mobilephone: Optional[
        constr(regex=regexes.MOBILEPHONE_NUMBER, strip_whitespace=True)
    ]
    email: Optional[EmailStr]
    contact_type: ContactType

    @root_validator(pre=True)
    def validate_atleast_one_way_to_contact(cls, values):
        telephone = values.get("telephone")
        mobilephone = values.get("mobilephone")
        email = values.get("email")
        if not telephone and not mobilephone and not email:
            raise ValueError(_("Enter at least telephone or mobilephone or email."))
        return values


def required_contact_input_wrapper(**kwargs):
    try:
        return RequiredContactInput(**kwargs)
    except ValidationError as e:
        try:
            root_err = next(filter(lambda e: e._loc == ("__root__"), e.raw_errors))
            e._error_cache = None
            root_err._loc = ("telephone",)
        except StopIteration:
            pass
        raise e
