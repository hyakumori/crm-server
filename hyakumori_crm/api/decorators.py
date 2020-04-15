import inspect
from functools import wraps

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_typed_views.decorators import prevalidate, transform_view_params
from rest_typed_views.utils import find_request


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
