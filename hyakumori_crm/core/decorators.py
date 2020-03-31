from functools import wraps
from datetime import datetime
import pytz
from pydantic import ValidationError


def validate_model(input_model, get_func=None):
    def decorator(resolver):
        @wraps(resolver)
        def decorated_function(_, info, **kwargs) -> dict:
            try:
                data = kwargs["data"]
                pk = kwargs.get("pk")
                if pk:
                    # when update instance, add instance context for validator
                    assert get_func is not None, "get_func can't be None"
                    instance = get_func(pk=pk)
                    if not instance:
                        return {"ok": False, "error": {"msg": "Not found"}}
                    data["context"] = {"updated_at": instance.updated_at}

                    del kwargs["pk"]
                    kwargs["instance"] = instance

                validated_data = input_model(**data).dict()
            except ValidationError as e:
                return {"ok": False, "error": e.errors()}

            kwargs["data"] = validated_data
            try:
                output = resolver(_, info, **kwargs)
            except Exception as e:
                return {"ok": False, "error": dict(message=str(e))}
            return {"ok": True, **output}

        return decorated_function

    return decorator
