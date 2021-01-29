import operator
from enum import Enum
from functools import reduce
from typing import List, Optional
from uuid import UUID

from django.core.exceptions import ValidationError as DjValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from pydantic import EmailStr, constr, root_validator, validator
from rest_framework.serializers import ModelSerializer, UUIDField

from ..core.models import HyakumoriDanticModel, Paginator
from ..crm.common import regexes
from ..crm.common.constants import DEFAULT_EMAIL, EMPTY, UNKNOWN
from ..crm.common.utils import tags_csv_to_dict
from ..crm.models import Contact, Customer, Forest, ForestCustomer
from rest_framework_gis.fields import GeometryField


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
    postal_code: Optional[constr(regex=regexes.POSTAL_CODE, strip_whitespace=True)]
    address: Optional[Address] = {}
    telephone: Optional[constr(regex=regexes.TELEPHONE_NUMBER, strip_whitespace=True)]
    mobilephone: Optional[
        constr(regex=regexes.MOBILEPHONE_NUMBER, strip_whitespace=True)
    ]
    email: Optional[EmailStr] = DEFAULT_EMAIL


class BankingInput(HyakumoriDanticModel):
    account_designator: Optional[str]
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


class CustomerPaginator(Paginator):
    @validator("filters")
    def validate_filters(cls, filters_input):
        defined_filters = []
        for k, value in filters_input.items():
            values = list(set(map(lambda v: v.strip(), value.split(","))))
            if len(values) == 1 and values[0] == "":
                if k == "tags":
                    name = "tags_repr"
                else:
                    name = k
                conditions = Q(**{f"{name}__exact": None})
            else:
                if k == "tags":
                    search_field_filter = "tags_repr__icontains"
                else:
                    search_field_filter = k + "__icontains"
                conditions = reduce(
                    operator.or_,
                    (
                        *[
                            Q(**{search_field_filter: value})
                            for value in values
                            if len(value) > 0
                        ],
                        *(
                            [
                                Q(**{"forest_tags_repr__icontains": value})
                                for value in values
                                if len(value) > 0
                            ]
                            if k == "tags"
                            else []
                        ),
                    ),
                )
            defined_filters.append(conditions)

        if len(defined_filters) > 0:
            return reduce(operator.and_, defined_filters)
        return defined_filters


class ForestSerializer(ModelSerializer):
    forestcustomer_id = UUIDField(read_only=True)
    geodata = GeometryField(allow_null=True, required=False, source="geodata4326")

    class Meta:
        model = Forest
        fields = [
            "id",
            "cadastral",
            "internal_id",
            "customers_count",
            "forestcustomer_id",
            "land_attributes",
            "tags",
            "attributes",
            "geodata",
        ]


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


class NonDirectContactType(str, Enum):
    family = "FAMILY"
    others = "OTHERS"


class SingleSelectContactInput(HyakumoriDanticModel):
    contact: Contact
    relationship_type: Optional[RelationshipType]

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
    contact_type: ContactType
    forest_id: Optional[UUID]

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

    @root_validator
    def validate_contact_type_and_forest_id(cls, values):
        contact_type = values.get("contact_type")
        forest_id = values.get("forest_id")
        if not contact_type:
            return values
        if contact_type == ContactType.forest and not forest_id:
            raise ValueError(_("forest_id not provied for contact_type FOREST"))
        elif (
            contact_type == ContactType.forest
            and forest_id not in cls.customer_forest_pks
        ):
            raise ValueError(_("customer does not have supplied forest_id"))
        return values

    @validator("deleting", each_item=True)
    def validate_deleting_contact_ids(cls, v):
        if v not in cls.customer_contact_pks:
            raise ValueError(_("Contact {} not found").format(v))
        return v


class CustomerMemoInput(HyakumoriDanticModel):
    customer: Customer
    memo: str = None

    class Config:
        arbitrary_types_allowed = True
        min_anystr_length = 0


class RequiredContactInput(HyakumoriDanticModel):
    name_kanji: Name
    name_kana: Name
    postal_code: Optional[constr(regex=regexes.POSTAL_CODE, strip_whitespace=True)]

    address: Optional[Address] = {}
    telephone: Optional[constr(regex=regexes.TELEPHONE_NUMBER, strip_whitespace=True)]

    mobilephone: Optional[
        constr(regex=regexes.MOBILEPHONE_NUMBER, strip_whitespace=True)
    ]
    email: Optional[EmailStr]
    contact_type: NonDirectContactType

    # @root_validator
    # def validate_atleast_one_way_to_contact(cls, values):
    #     telephone = values.get("telephone")
    #     mobilephone = values.get("mobilephone")
    #     email = values.get("email")
    #     if not telephone and not mobilephone and not email:
    #         raise ValueError(_("Enter at least telephone or mobilephone or email."))
    #     return values


class CustomerUploadCsv(HyakumoriDanticModel):
    business_id: Optional[
        constr(regex=regexes.CUSTOMER_ID, strip_whitespace=True)
    ] = EMPTY
    fullname_kana: str
    fullname_kanji: str
    prefecture: Optional[str] = EMPTY
    municipality: Optional[str] = EMPTY
    sector: Optional[str]
    postal_code: Optional[
        constr(regex=regexes.POSTAL_CODE, strip_whitespace=True)
    ] = EMPTY

    telephone: Optional[
        constr(regex=regexes.CSV_TELEPHONE_NUMBER, strip_whitespace=True)
    ] = EMPTY

    mobilephone: Optional[
        constr(regex=regexes.MOBILEPHONE_NUMBER, strip_whitespace=True)
    ] = EMPTY
    email: Optional[EmailStr] = EMPTY
    bank_name: Optional[str] = EMPTY
    bank_branch_name: Optional[str] = EMPTY
    bank_account_type: Optional[str] = EMPTY
    bank_account_number: Optional[constr(regex=regexes.BANKING_ACCOUNT_NUMBER)]
    bank_account_name: Optional[str] = EMPTY
    tags: Optional[str]

    class Config:
        error_msg_templates = {
            **HyakumoriDanticModel.Config.error_msg_templates,
            "value_error.str.regex.telephone": _(
                "Bad format (000-000-0000 or 00-0000-0000 or 0000000000)."
            ),
            "value_error.str.regex.postal_code": _("Bad format (000-0000)."),
            "value_error.str.regex.mobilephone": _("Bad format (000-0000-0000)."),
        }

    @validator("bank_account_number", pre=True)
    def prepare_account_number(cls, v):
        return v[1:-1]

    @validator("tags")
    def tags_validator(cls, value):
        try:
            tags_csv_to_dict(value)
        except ValueError:
            raise ValueError(_("Invalid format (tag1:value1; tag2:value2)"))
        return value

    @property
    def name_kana(self):
        name_parts = self.fullname_kana.split("\u3000")
        if len(name_parts) == 2:
            return {"first_name": name_parts[1], "last_name": name_parts[0]}
        return {"first_name": "", "last_name": name_parts[0]}

    @property
    def name_kanji(self):
        name_parts = self.fullname_kanji.split("\u3000")
        if len(name_parts) == 2:
            return {"first_name": name_parts[1], "last_name": name_parts[0]}
        return {"first_name": "", "last_name": name_parts[0]}

    @property
    def address(self):
        return {
            "prefecture": self.prefecture,
            "municipality": self.municipality,
            "sector": self.sector,
        }

    @property
    def banking(self):
        return {
            "bank_name": self.bank_name,
            "branch_name": self.bank_branch_name,
            "account_type": self.bank_account_type,
            "account_number": self.bank_account_number,
            "account_name": self.bank_account_name,
        }

    @property
    def tags_json(self):
        return tags_csv_to_dict(self.tags)
