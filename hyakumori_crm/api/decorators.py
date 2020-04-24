import inspect
import logging
from functools import wraps
from typing import Callable

from pydantic import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_typed_views.decorators import prevalidate, transform_view_params
from rest_typed_views.utils import find_request

from hyakumori_crm.core.decorators import errors_wrapper

logger = logging.getLogger(__name__)


def typed_api_view(methods, permissions_classes=None):
    if permissions_classes is None:
        permissions_classes = [IsAuthenticated]

    def wrap_validate_and_render(view):
        prevalidate(view)

        @api_view(methods)
        @permission_classes(permissions_classes)
        @wraps(view)
        def wrapper(*original_args, **original_kwargs):
            original_args = list(original_args)
            request = find_request(original_args)
            transformed = transform_view_params(
                inspect.signature(view).parameters.values(), request, original_kwargs
            )
            return view(*transformed)

        return wrapper

    return wrap_validate_and_render


def get_or_404(
    get_func: Callable,
    to_name: str,
    pass_to: str = "request",
    msg: str = None,
    remove: bool = False,
):
    """Get model instance base on kwargs passed from url and inject into `request.data`.
    Raise Http404 if not found.
    If `remove`, url params will be removed from kwargs pass to view function."""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if len(args) == 1:
                request = args[0]
            elif len(args) == 2:
                # in case of class method , `self` is first arg
                request = args[1]
            else:
                raise TypeError(
                    "Invalid func arguments, only kwargs after request param"
                )

            try:
                get_func_args = {
                    arg: kwargs[arg] for arg in inspect.getfullargspec(get_func).args
                }
            except KeyError:
                return

            try:
                obj = get_func(**get_func_args)
            except ValueError as e:
                raise NotFound(msg or str(e))

            obj_passed = False
            if (pass_to == "request" or "request" in pass_to) and request.method in [
                "POST",
                "PUT",
                "PATCH",
            ]:
                # currently only work if content-type is application/json
                request.data[to_name] = obj
                obj_passed = True
            if pass_to == "kwargs" or "kwargs" in pass_to:
                kwargs[to_name] = obj
                obj_passed = True
            if pass_to == "kwargs_data" or "kwargs_data" in pass_to:
                if "_data" not in kwargs:
                    kwargs["_data"] = request.data.copy()
                kwargs["_data"][to_name] = obj
                obj_passed = True

            if remove and obj_passed:
                for arg in get_func_args:
                    del kwargs[arg]

            return f(*args, **kwargs)

        return wrapper

    return decorator


def api_validate_model(input_model, arg_name="data"):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs) -> dict:
            if len(args) == 1:
                request = args[0]
            elif len(args) == 2:
                # in case of class method , `self` is first arg
                request = args[1]
            else:
                raise TypeError(
                    "Invalid func arguments, only kwargs after request param"
                )
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    validated_input = input_model(**request.data)
                    kwargs[arg_name] = validated_input
                except ValidationError as e:
                    return Response({"errors": errors_wrapper(e.errors())}, status=400)

            try:
                return f(*args, **kwargs)
            except Exception as e:
                logger.exception(e)
                # sentry logs etc.
                return Response({"errors": dict(message=str(e))}, status=500)

        return wrapper

    return decorator


# TODO: implement policies check
def action_login_required(with_policies=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    return decorator
