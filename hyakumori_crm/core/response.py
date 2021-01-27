import django.http
import json
import orjson

from collections import OrderedDict
from django.contrib.gis.geos.collections import MultiPolygon
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.utils.serializer_helpers import ReturnList


class CustomDjangoJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, ReturnList):
            return list(o)
        elif isinstance(o, OrderedDict):
            return dict(o)
        elif isinstance(o, MultiPolygon):
            return json.loads(o.transform(4326, clone=True).geojson)
        else:
            DjangoJSONEncoder.default(self, o)


class OrjsonResponse(django.http.HttpResponse):
    def __init__(
        self,
        data,
        encoder=CustomDjangoJSONEncoder,
        safe=True,
        json_dumps_params=None,
        **kwargs
    ):
        if safe and not isinstance(data, dict):
            raise TypeError(
                "In order to allow non-dict objects to be serialized set the "
                "safe parameter to False."
            )
        if json_dumps_params is None:
            json_dumps_params = {}
        kwargs.setdefault("content_type", "application/json")
        data = orjson.dumps(data, default=encoder().default, **json_dumps_params)
        super().__init__(content=data, **kwargs)


# monkey-patching django's JsonResponse
django.http.JsonResponse = OrjsonResponse
