from .models import Forest
from django.core.exceptions import ValidationError
from django.conf import settings
import json
import os

def get_all():
    dump_total = 50
    dummyDataPath = os.path.join(settings.BASE_DIR, "hyakumori_crm/dummy", "forest_data.json")
    with open(dummyDataPath, 'r') as file:
        if file is None:
            return {
                "ok": False,
                "forests": None,
                "total": 0
            }
        else:
            data = file.read()
            forests = json.loads(data)
            file.close()
            return {
                "ok": True,
                "forests": forests if forests else None,
                "total": dump_total
            }

def get(pk):
    try:
        return Forest.objects.get(pk=pk)
    except (Forest.DoesNotExist, ValidationError):
        return None

def create(data):
    forest = Forest(**data)
    forest.save()
    return forest

