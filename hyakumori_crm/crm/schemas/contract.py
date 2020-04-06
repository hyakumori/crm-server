from datetime import date, datetime
from typing import Union

from pydantic import BaseModel

from hyakumori_crm.crm.common.constants import EMPTY


class Contract(BaseModel):
    """
    契約
    長期契約	長期契約日	作業道契約	作業道契約日	FSC認証加入	FSC認証加入日
    """

    long_term_contract: Union[bool, str, None] = EMPTY
    long_term_contract_date: Union[date, datetime, None] = None
    work_road_contract: Union[bool, str, None] = EMPTY
    work_road_contract_date: Union[date, datetime, None] = None
    fsc_certificate: Union[bool, str, None] = EMPTY
    fsc_certificate_date: Union[date, datetime, None] = None
