from uuid import uuid4

import pandas as pd

from hyakumori_crm.crm.common.constants import CUSTOMER_TAG_KEYS
from hyakumori_crm.crm.schemas.customer import (
    Address,
    Banking,
    Contact,
    CustomerSchema,
    Name,
)
from pandas import DataFrame
from pydantic import ValidationError

from ..lib.common import Counter
from ..lib.utils import get_or_default, normalize, process_nan_id
from .base import BaseImporter


class CustomerImporter(BaseImporter):
    def __init__(self, df: DataFrame):
        # skip second row as sub header row
        self.datasource = df.iloc[1:, 0:21]
        self.datasource = self.datasource.where(pd.notnull(df), None)
        self.datasource.header = None
        self.datasource.columns = [
            "internal_id",
            "新規ID発行",
            "所有者１_kanji_lastname",
            "所有者１_kanji_firstname",
            "所有者１_kana_lastname",
            "所有者１_kana_firstname",
            "都道府県",
            "市町村",
            "大字/字",
            "郵便番号",
            "電話番号",
            "携帯電話",
            "メールアドレス",
            "銀行名",
            "支店名",
            "種類",
            "口座番号",
            "口座名義",
            "未登録/登録",
            "所有者順位",
            "同姓同名",
        ]
        self.results = dict()
        self.counter = None

    def build(self, row):
        name_kanji = Name(
            first_name=normalize(row["所有者１_kanji_firstname"]),
            last_name=normalize(row["所有者１_kanji_lastname"]),
        )
        name_kana = Name(
            first_name=normalize(row["所有者１_kana_firstname"]),
            last_name=normalize(row["所有者１_kana_lastname"]),
        )
        address = Address(
            prefecture=row["都道府県"], municipality=row["市町村"], sector=row["大字/字"],
        )
        contact = Contact(
            name_kanji=name_kanji,
            name_kana=name_kana,
            postal_code=get_or_default(row["郵便番号"], None),
            telephone=row["電話番号"],
            mobilephone=row["携帯電話"],
            email=row["メールアドレス"],
            address=address,
        )
        banking = Banking(
            bank_name=row["銀行名"],
            branch_name=row["支店名"],
            account_type=row["種類"],
            account_number=row["口座番号"],
            account_name=row["口座名義"],
        )
        tags_name = CUSTOMER_TAG_KEYS.values() # ["未登録/登録", "所有者順位", "同姓同名"]
        tags = dict(zip(tags_name, [get_or_default(row[tag], None) for tag in tags_name]))
        internal_id = process_nan_id(row["internal_id"])

        return CustomerSchema(
            id=uuid4().hex,
            internal_id=str(internal_id),
            name_kana=name_kana,
            name_kanji=name_kanji,
            address=address,
            basic_contact=contact,
            banking=banking,
            tags=tags,
        )

    def run(self):
        self.counter = Counter()
        self.counter.set_total(self.datasource.shape[0])

        for _, row in self.datasource.iterrows():
            print(f"importing {process_nan_id(row[0])} ... ", end="", flush=True)
            self.counter.mark_processed()
            try:
                data = self.build(row)
                row_id = (
                    data.id
                    if data.internal_id is None or len(data.internal_id) == 0
                    else data.internal_id
                )
                self.results[row_id] = data
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
