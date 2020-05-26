import csv
import json
import time

from django.db import OperationalError, transaction
from django.utils.translation import gettext_lazy as _
import pydantic

from hyakumori_crm.core.decorators import errors_wrapper
from hyakumori_crm.crm.models import Customer, Forest

from .schemas import CustomerUploadCsv
from .service import save_customer_from_csv_data
from ..cache.forest import refresh_customer_forest_cache


def csv_upload(fp):
    header_map = {
        "business_id": "所有者ID",
        "fullname_kana": "土地所有者名（漢字）",
        "fullname_kanji": "土地所有者名（カナ）",
        "prefecture": "土地所有者住所_都道府県",
        "municipality": "土地所有者住所_市町村",
        "sector": "土地所有者住所_大字",
        "postal_code": "連絡先情報_郵便番号",
        "telephone": "連絡先情報_電話番号",
        "mobilephone": "連絡先情報_携帯電話",
        "email": "連絡先情報_メールアドレス",
        "bank_name": "口座情報_銀行名",
        "bank_branch_name": "口座情報_支店名",
        "bank_account_type": "口座情報_種別",
        "bank_account_number": "口座情報_口座番号",
        "bank_account_name": "口座情報_口座名義",
        "tags": _("Tag"),
    }
    with open(fp, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        line_count = 0
        customer_ids = []
        for row in reader:
            if line_count == 0:
                line_count += 1
            row_data = {k: row[v] for k, v in header_map.items()}
            try:
                c = Customer.objects.select_for_update(nowait=True).get(
                    business_id=row_data["business_id"]
                )
                customer_ids.append(c.id)
            except Customer.DoesNotExist:
                return {"errors": {"__root__": ["Customer not found"]}}
            except OperationalError:
                return {
                    "errors": {
                        "__root__": ["Current resources are not ready for update!!"]
                    }
                }
            else:
                try:
                    customer_data = CustomerUploadCsv(**row_data)
                    save_customer_from_csv_data(c, customer_data)
                except pydantic.ValidationError as e:
                    errors = {}
                    for key, msgs in errors_wrapper(e.errors()).items():
                        if key == "__root__":
                            errors[key] = msgs
                        else:
                            errors[header_map[key]] = msgs
                    return {"line": line_count + 1, "errors": errors}
            line_count += 1
        fids = Forest.objects.filter(
            forestcustomer__customer_id__in=customer_ids
        ).values_list("id", flat=True)
        refresh_customer_forest_cache(fids)
    return line_count
