from enum import Enum
from typing import List, Union

from pydantic import BaseModel, EmailStr, constr

from ..common import regexes
from ..common.constants import DEFAULT_EMAIL, EMPTY, UNKNOWN


class Name(BaseModel):
    first_name: Union[str, None] = EMPTY
    last_name: Union[str, None] = EMPTY


class Address(BaseModel):
    """
    土地所有者住所
    都道府県	市町村	大字/字
    """

    prefecture: Union[str, None] = UNKNOWN
    municipality: Union[str, None] = EMPTY
    sector: Union[str, None] = EMPTY


class Contact(BaseModel):
    """
    連絡先情報
    郵便番号	電話番号	携帯電話	メールアドレス
    """

    name_kanji: Name = Name()
    name_kana: Name = Name()
    postal_code: Union[
        constr(regex=regexes.POSTAL_CODE, strip_whitespace=True), None
    ] = "000-0000"
    telephone: Union[
        constr(regex=regexes.TELEPHONE_NUMBER, strip_whitespace=True), None
    ] = "00-0000-0000"
    mobilephone: Union[
        constr(regex=regexes.MOBILEPHONE_NUMBER, strip_whitespace=True), None
    ] = None
    email: Union[EmailStr, None] = None
    address: Address = Address()


class Banking(BaseModel):
    """
    口座情報
    銀行名	支店名	種類	口座番号	口座名義
    """

    bank_name: Union[str, None] = UNKNOWN
    branch_name: Union[str, None] = UNKNOWN
    account_type: Union[str, None] = EMPTY
    account_number: Union[constr(regex=regexes.BANKING_ACCOUNT_NUMBER), None] = None
    account_name: Union[str, None] = UNKNOWN


class CustomerStatus(str, Enum):
    registered = "登録済"
    unregistered = "未登録"


class CustomerSchema(BaseModel):
    id: str
    internal_id: Union[str, None] = EMPTY
    name_kanji: Name = Name()
    name_kana: Name = Name()
    address: Address
    basic_contact: Contact = Contact()
    contacts: List[Contact] = []
    banking: Banking
    tags: List[str] = []
    status: CustomerStatus = CustomerStatus.unregistered
