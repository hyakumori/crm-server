"""
土地管理ID	地籍    土地所有者名	土地所有者住所  契約    タグ    森林情報
    都道府県	市町村	大字	字	漢字	カナ	郵便番号	都道府県	市町村
    大字/字	長期契約	長期契約日	作業道契約	作業道契約日	FSC認証加入	FSC認証加入日
    団地	管理形態	面積_ha	面積_m2	平均傾斜度	第1林相ID	第1林相名	第1Area	第1面積_ha
    第1立木本	第1立木密	第1平均樹	第1樹冠長	第1平均DBH	第1合計材	第1ha材積	第1収量比
    第1相対幹	第1形状比	第2林相ID	第2林相名	第2Area	第2面積_ha	第2立木本	第2立木密
    第2平均樹	第2樹冠長	第2平均DBH	第2合計材	第2ha材積	第2収量比	第2相対幹	第2形状比
    第3林相ID	第3林相名	第3Area	第3面積_ha	第3立木本	第3立木密	第3平均樹	第3樹冠長
    第3平均DBH	第3合計材	第3ha材積	第3収量比	第3相対幹	第3形状比

"""
from typing import Any, List, Union

from pydantic import BaseModel
from typing_extensions import Literal

from ..common.constants import EMPTY, UNKNOWN
from .contract import Contract
from .customer import Address, Name


class Cadastral(BaseModel):
    """
    地籍
    都道府県	市町村	大字	字
    """

    prefecture: Union[str, None] = UNKNOWN
    municipality: Union[str, None] = EMPTY
    sector: Union[str, None] = EMPTY
    subsector: Union[str, None] = EMPTY


class ForestOwner(BaseModel):
    """
    土地所有者住所
    郵便番号	都道府県	市町村	大字/字
    """
    name_kanji: Union[Name, str, None] = Name()
    name_kana: Union[Name, str, None] = Name()
    address: Address = Address()


class Tag(BaseModel):
    """
    タグ
    団地	管理形態
    """

    danchi: Union[str, None] = EMPTY
    manage_type: Union[str, None] = EMPTY


class LandAttribute(BaseModel):
    key: Literal["地番本番", "地番支番", "地目", "林班", "小班", "区画"]
    value: Any


class ForestAttribute(BaseModel):
    key: Literal[
        "地番面積_ha",
        "面積_ha",
        "面積_m2",
        "平均傾斜度",
        "第1林相ID",
        "第1林相名",
        "第1Area",
        "第1面積_ha",
        "第1立木本",
        "第1立木密",
        "第1平均樹",
        "第1樹冠長",
        "第1平均DBH",
        "第1合計材",
        "第1ha材積",
        "第1収量比",
        "第1相対幹",
        "第1形状比",
        "第2林相ID",
        "第2林相名",
        "第2Area",
        "第2面積_ha",
        "第2立木本",
        "第2立木密",
        "第2平均樹",
        "第2樹冠長",
        "第2平均DBH",
        "第2合計材",
        "第2ha材積",
        "第2収量比",
        "第2相対幹",
        "第2形状比",
        "第3林相ID",
        "第3林相名",
        "第3Area",
        "第3面積_ha",
        "第3立木本",
        "第3立木密",
        "第3平均樹",
        "第3樹冠長",
        "第3平均DBH",
        "第3合計材",
        "第3ha材積",
        "第3収量比",
        "第3相対幹",
        "第3形状比",
    ]
    value: Any


class ForestSchema(BaseModel):
    internal_id: str = EMPTY
    cadastral: Cadastral = Cadastral()
    original_owner: ForestOwner
    owners: List[ForestOwner] = []
    contracts: List[Contract] = []
    tag: Tag = Tag()
    land_attributes: List[LandAttribute] = []
    forest_attributes: List[ForestAttribute] = []


class GeoData(BaseModel):
    latitude: Union[float, None]
    longitude: Union[float, None]
