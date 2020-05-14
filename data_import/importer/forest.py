import pandas as pd

from hyakumori_crm.crm.common.constants import FOREST_TAG_KEYS
from hyakumori_crm.crm.schemas.contract import ContractType
from hyakumori_crm.crm.schemas.forest import (
    Address,
    Cadastral,
    Contract,
    ForestAttribute,
    ForestOwner,
    ForestSchema,
    LandAttribute,
    Name,
    Tags,
)
from pandas import DataFrame
from pydantic import ValidationError

from ..lib.common import Counter
from ..lib.utils import normalize, process_date, process_nan_id, get_or_default
from .base import BaseImporter


class ForestImporter(BaseImporter):
    def __init__(self, df: DataFrame):
        self._config_datasource(df)
        self.results = dict()
        self.counter = None

    def _config_datasource(self, df):
        self.datasource = df.iloc[1:]
        self.datasource = self.datasource.where(pd.notnull(df), None)
        self.datasource.header = None
        # This list is copied from xlsx file with some edit on empty/duplicated columns
        self.datasource.columns = [
            "土地管理ID",
            "都道府県",
            "市町村",
            "大字",
            "字",
            "地番本番",
            "地番支番",
            "地目",
            "林班",
            "小班",
            "区画",
            "owner_漢字",
            "owner_カナ",
            "owner_都道府県",
            "owner_市町村",
            "owner_大字/字",
            "所有者1_kanji_lastname",
            "所有者1_kanji_firstname",
            "所有者2_kanji_lastname",
            "所有者2_kanji_firstname",
            "所有者3_kanji_lastname",
            "所有者3_kanji_firstname",
            "所有者4_kanji_lastname",
            "所有者4_kanji_firstname",
            "所有者1_kana_lastname",
            "所有者1_kana_firstname",
            "所有者2_kana_lastname",
            "所有者2_kana_firstname",
            "所有者3_kana_lastname",
            "所有者3_kana_firstname",
            "所有者4_kana_lastname",
            "所有者4_kana_firstname",
            "長期契約",
            "長期契約_開始日",
            "長期契約_終了日",
            "作業道契約",
            "作業道契約_開始日",
            "作業道契約_終了日",
            "FSC認証加入",
            "FSC認証加入_開始日",
            "FSC認証加入_終了日",
            "団地",
            "管理形態",
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

    def _build_status(self, value):
        mapping = {
            "期限切り": "期限切",
            "締結中": "契約済",
            "交渉中": "未契約",
            "未締結": "未契約",
        }

        return mapping.get(value, None)

    def _build_land_attributes(self, row):
        columns = tuple(self.datasource.columns)
        start_index = columns.index("地番本番")
        end_index = columns.index("区画")
        result = []
        for index in range(start_index, end_index + 1):
            column = columns[index]
            land_attribute = LandAttribute(key=column, value=row[column])
            result.append(land_attribute)
        return result

    def _build_forest_attributes(self, row):
        columns = tuple(self.datasource.columns)
        start_index = columns.index("地番面積_ha")
        result = []
        for index in range(start_index, len(self.datasource.columns)):
            column = columns[index]
            forest_attribute = ForestAttribute(key=column, value=row[column])
            result.append(forest_attribute)

        return result

    def _build_owners(self, row):
        _indexes = ["1", "2", "3", "4"]
        _name_template = "所有者{index}_{type}_{name_part}name"
        result = []
        for index in _indexes:
            _owner = ForestOwner(
                name_kanji=Name(
                    first_name=normalize(row[_name_template.format(index=index, type="kanji", name_part="first")]),
                    last_name=normalize(row[_name_template.format(index=index, type="kanji", name_part="last")])
                ),
                name_kana=Name(
                    first_name=normalize(row[_name_template.format(index=index, type="kana", name_part="first")]),
                    last_name=normalize(row[_name_template.format(index=index, type="kana", name_part="last")])
                ),
                address=Address(
                    prefecture=row["owner_都道府県"],
                    municipality=row["owner_市町村"],
                    sector=row["owner_大字/字"],
                ),
            )
            if _owner.name_kanji.last_name is None and _owner.name_kanji.first_name is None:
                continue

            result.append(_owner)

        return result

    def build(self, row):
        internal_id = process_nan_id(row["土地管理ID"])
        cadastral = Cadastral(
            prefecture=row["都道府県"],
            municipality=row["市町村"],
            sector=row["大字"],
            subsector=row["字"],
        )
        original_owner = ForestOwner(
            name_kanji=normalize(row["owner_漢字"]),
            name_kana=normalize(row["owner_カナ"]),
            address=Address(
                prefecture=row["owner_都道府県"],
                municipality=row["owner_市町村"],
                sector=row["owner_大字/字"],
            ),
        )
        contracts = [
            Contract(
                type=ContractType.long_term,
                status=self._build_status(row["長期契約"]),
                start_date=process_date(row["長期契約_開始日"]),
                end_date=process_date(row["長期契約_終了日"]),
            ),
            Contract(
                type=ContractType.work_road,
                status=self._build_status(row["作業道契約"]),
                start_date=process_date(row["作業道契約_開始日"]),
                end_date=process_date(row["作業道契約_終了日"]),
            ),
            Contract(
                type=ContractType.fsc,
                status=self._build_status(row["FSC認証加入"]),
                start_date=process_date(row["FSC認証加入_開始日"]),
                end_date=process_date(row["FSC認証加入_終了日"]),
            ),
        ]
        tags_name = FOREST_TAG_KEYS.values()  # ["未登録/登録", "所有者順位", "同姓同名"]
        tags = dict(zip(tags_name, [get_or_default(row[tag], None) for tag in tags_name]))
        forest_attributes = self._build_forest_attributes(row)
        land_attributes = self._build_land_attributes(row)

        owners = self._build_owners(row)

        return ForestSchema(
            internal_id=str(internal_id),
            cadastral=cadastral,
            original_owner=original_owner,
            owners=owners,
            contracts=contracts,
            tags=tags,
            land_attributes=land_attributes,
            forest_attributes=forest_attributes,
        )

    def run(self):
        self.counter = Counter()
        self.counter.set_total(self.datasource.shape[0])

        for _, row in self.datasource.iterrows():
            print(f"importing {process_nan_id(row[0])} ... ", end="", flush=True)
            self.counter.mark_processed()
            try:
                data = self.build(row)
                iid = data.internal_id
                if iid not in self.results.keys():
                    self.results[iid] = data
                print("OK")
                self.counter.mark_succeed()
            except ValidationError as e:
                self.counter.mark_error()
                print("ERROR", e)
                c = input("continue? ")
                if len(c) > 0:
                    break
                continue

        print(self.counter)

    def validate(self):
        if len(self.results) == 0:
            raise ValueError("Please run import first")
        assert self.counter.processed == self.counter.success

        print("Data import finished without error")
