from typing import Union
from ariadne import ScalarType

json_scalar = ScalarType("JSON")


@json_scalar.serializer
def serialize_json(value: Union[dict, None]):
    return value
