from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, EmailStr, constr, validator

from ..core.models import HyakumoriDanticModel, HyakumoriDanticUpdateModel
from ..crm.common import regexes
from ..crm.common.constants import DEFAULT_EMAIL, EMPTY, UNKNOWN


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
