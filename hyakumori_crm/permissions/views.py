from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes

from ..core.utils import make_success_json
from ..core.permissions import AdminGroupPermission

from .services import PermissionService


@api_view(["GET"])
@permission_classes([AdminGroupPermission])
def get_resource_permissions(request: Request):
    permissions = PermissionService.get_app_permissions(app_label="crm")
    return make_success_json(data=dict(permissions=permissions))


@api_view(["GET"])
@permission_classes([AdminGroupPermission])
def get_groups(request: Request):
    groups = PermissionService.get_groups()
    return make_success_json(data=dict(groups=groups))
