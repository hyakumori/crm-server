from .models import Forest
from django.core.exceptions import ValidationError
from django.conf import settings
import json
import os


def get_all():
    dump_total = 50
    dummyDataPath = os.path.join(
        settings.BASE_DIR, "hyakumori_crm/dummy", "forest_data.json"
    )
    try:
        with open(dummyDataPath, "r") as file_obj:
            forests = json.load(file_obj)
            return {
                "ok": True,
                "forests": forests,
                "total": dump_total,
            }
    except (FileNotFoundError, json.JSONDecodeError):
        return {"ok": False, "forests": None, "total": 0}


def get(pk):
    try:
        return Forest.objects.get(pk=pk)
    except (Forest.DoesNotExist, ValidationError):
        return None


def create(data):
    forest = Forest(**data)
    forest.save()
    return forest
