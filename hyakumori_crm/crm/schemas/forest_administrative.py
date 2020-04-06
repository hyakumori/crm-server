"""
[DEPRECATED]
Keep for reference as fulfill master data import
"""

from typing import Any, List, Union

from pydantic import BaseModel
from typing_extensions import Literal

from ..common.constants import EMPTY
from .contract import Contract
from .customer import Address, Name


class CustomAddress(Address):
    sector2: Union[str, None] = None


class Owner(BaseModel):
    """
    土地所有者名漢字	土地所有者名カナ
    土地所有者名の在村不在村	土地所有者都道府県	土地所有者市町村
    土地所有者住所1	土地所有者住所2
    """

    name: Name = Name()
    absent_status: Union[str, None] = None
    address: CustomAddress = CustomAddress()


class LandAttribute(BaseModel):
    key: Literal[
        "地番データ時点", "都道府県", "市町村", "大字", "字", "地番本番", "地番支番", "地目", "林班", "小班", "区画"
    ]
    value: Any


class ForestAttribute(BaseModel):
    key: Literal["地番面積", "分収林", "森林の種類範囲 第1", "森林の種類範囲 第2", "森林の種類範囲 第3"]
    value: Any


class ForestAdministrative(BaseModel):
    """
    土地管理ID
    ---
    長期契約	長期契約日	作業道契約	作業道契約日	FSC認証加入	FSC認証加入日
    ---
    地番データ時点	都道府県	市町村	大字	字	地番本番	地番支番	地目	林班	小班	区画
    ---
    土地所有者名漢字	土地所有者名カナ
    土地所有者名の在村不在村	土地所有者都道府県	土地所有者市町村
    土地所有者住所1	土地所有者住所2
    ---
    地番面積	分収林	森林の種類範囲 第1	森林の種類範囲 第2	森林の種類範囲 第3
    """

    internal_id: str = EMPTY
    contract: Contract = Contract()
    owner: Owner = Owner()
    land_attributes: List[LandAttribute] = []
    forest_attributes: List[ForestAttribute] = []
