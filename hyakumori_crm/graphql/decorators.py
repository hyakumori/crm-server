from functools import wraps

from django.http import HttpRequest
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from hyakumori_crm.permissions.services import PermissionService


def login_required(with_policies=None):
    """Requires login for a resolver"""

    def decorator(resolver):

        @wraps(resolver)
        def wrapper(parent, info, *args, **kwargs):

            if isinstance(info.context, HttpRequest):
                authenticator = JWTAuthentication()
                auth_result = authenticator.authenticate(info.context)

                if auth_result is None:
                    raise PermissionDenied()

                user, _ = auth_result

                if not user.is_authenticated:
                    raise NotAuthenticated()

                if with_policies is not None and len(with_policies) > 0:
                    is_allowed_request = PermissionService.check_policies(info.context, user, with_policies)
                    if not is_allowed_request:
                        raise PermissionDenied()

                kwargs["current_user"] = user
                resolved = resolver(parent, info, *args, **kwargs)

            return resolved

        return wrapper

    return decorator
