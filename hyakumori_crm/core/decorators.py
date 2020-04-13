from datetime import datetime
from functools import wraps

import pytz
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


def errors_wrapper(errors):
    error_dict = {}
    for e in errors:
        key = ".".join(e["loc"])
        if key not in error_dict:
            error_dict[key] = [e["msg"]]
        else:
            error_dict[key].append(e["msg"])
    return error_dict


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

                validated_data = input_model(**data)
            except ValidationError as e:
                return {"ok": False, "error": errors_wrapper(e.errors())}

            kwargs["data"] = validated_data
            try:
                output = resolver(_, info, **kwargs)
            except Exception as e:
                logger.exception(e)
                # sentry logs etc.
                return {"ok": False, "error": dict(message=str(e))}
            return {"ok": True, **output}

        return decorated_function

    return decorator
