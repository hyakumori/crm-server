from rest_framework.request import Request
from rest_typed_views import CurrentUser

from hyakumori_crm.users.models import User
from .services import PermissionService
from ..api.decorators import typed_api_view
from ..core.utils import make_success_json


@typed_api_view(["GET"])
def get_resource_permissions(
    request: Request, user: User = CurrentUser(member_of="admin")
):
    permissions = PermissionService.get_app_permissions(app_label="crm")
    return make_success_json(data=dict(permissions=permissions))


@typed_api_view(["POST"])
def setup_groups(request: Request, user: User = CurrentUser()):
    groups = PermissionService.setup_groups(request.user)
    return make_success_json(data=dict(groups=groups))
