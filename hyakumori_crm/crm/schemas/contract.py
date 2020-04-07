from datetime import date, datetime
from enum import Enum
from typing import Union

from pydantic import BaseModel

from hyakumori_crm.crm.common.constants import EMPTY


class ContractType(str, Enum):
    long_term = "長期契約"
    work_road = "作業道契約"
    fsc = "FSC認証"


class Contract(BaseModel):
    """
    契約ステータス
    長期契約	開始日	終了日
    作業道契約	開始日	終了日
    FSC認証加入	開始日	終了日
    """
    type: ContractType = ContractType.long_term
    status: str = EMPTY
    start_date: Union[date, datetime, None] = None
    end_date: Union[date, datetime, None] = None
