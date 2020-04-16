import re
import unicodedata

import pandas as pd
import xlrd


def key_value_to_dict(kv_list):
    result = dict()
    for item in kv_list:
        result[item.key] = item.value

    return result


def c2i(c: str) -> int:
    return ord(c.lower()) - ord("a")


def cell_value(row, c: str):
    return row[c2i(c)]


def isempty(value):
    return pd.isnull(value) or pd.isna(value)


def read_date(date):
    return xlrd.xldate.xldate_as_datetime(date, 0)


def get_or_default(value, default_value):
    if isempty(value) or (isinstance(value, int) and value == 0):
        return default_value

    return value


def process_nan_id(internal_id):
    if isempty(internal_id):
        return ""

    return str(internal_id)


def process_date(value):
    _value = get_or_default(value, None)
    if _value is None:
        return None

    return read_date(_value)


def normalize(value):
    if value is None:
        return None

    normalized = unicodedata.normalize("NFKC", value)
    return normalized


def parse_name_extra(name):
    normalize_name = normalize(name)
    num = []
    if re.match(r"(外\d.+|他\d.+)$", normalize_name):
        num = re.findall(r"\d+", normalize_name)

    return int(num[0]) if len(num) > 0 else None


def prepare_env():
    from data_import.config import setup_django, setup_path

    setup_path()
    setup_django()
