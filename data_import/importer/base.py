import json

from django.core.serializers.json import DjangoJSONEncoder
from pydantic import BaseModel


class BaseImporter(object):
    def run(self):
        pass

    def build(self, row):
        pass

    def print_row(self, row: BaseModel):
        print(
            json.dumps(
                row.dict(),
                ensure_ascii=False,
                sort_keys=True,
                cls=DjangoJSONEncoder,
                indent=2,
            )
        )

    def validate(self):
        pass
