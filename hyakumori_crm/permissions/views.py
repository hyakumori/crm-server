from typing import List

from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from guardian.shortcuts import get_user_perms, get_group_perms, get_perms_for_model
from rest_framework.request import Request
from rest_framework.response import Response
from rest_typed_views import typed_api_view, Query, Path, CurrentUser

from hyakumori_crm.core.utils import model_to_dict
from hyakumori_crm.crm.models import Customer
from hyakumori_crm.users.models import User


@typed_api_view(["GET"])
def get_resource_permissions(request: Request, user: User = CurrentUser()):
    crm_content_types = ContentType.objects.filter(app_label="crm").all().values_list('id')
    permissions = [model_to_dict(permission) for permission in
                   Permission.objects.filter(content_type_id__in=crm_content_types).all().iterator()]
    return Response(permissions)


@typed_api_view(["GET"])
def get_user_permissions(request: Request, user: User = CurrentUser()):
    """
     Return
     list of user groups
     list of resource permission
     - forest
     - customer
     - archive
    :param request:
    :param user:
    :return:
    """

    user_groups = [model_to_dict(group) for group in user.groups.all().iterator()]
    customer_perms = [model_to_dict(perm, exclude="content_type,id") for perm in get_perms_for_model(Customer)]
    # user_perms = get_user_perms(user)
    # group_perms = get_group_perms(user)

    response = dict(
        is_admin=user.is_superuser,
        is_staff=user.is_staff,
        groups=user_groups,
        customer_perms=customer_perms
    )

    return Response(response)


@typed_api_view(["POST"])
def assign_user_resource_permissions(request: Request, permission_id: int, object_ids: List[int],
                                     user: User = CurrentUser(member_of="admin")):
    print(permission_id, object_ids)
    return Response()


@typed_api_view(["POST"])
def unassign_user_resource_permissions(request: Request, permission_id: int, object_ids: List[int],
                                       user: User = CurrentUser(member_of="admin")):
    print(permission_id, object_ids)
    return Response()


@typed_api_view(["POST"])
def add_user_group(request: Request, group_id: int, user: User = CurrentUser()):
    print(group_id)
    return Response()


@typed_api_view(["POST"])
def remove_user_group(request: Request, group_id: int, user: User = CurrentUser()):
    print(group_id)
    return Response()


@typed_api_view(["POST"])
def setup_groups(request: Request, user: User = CurrentUser()):
    if user.is_superuser:
        admin_group, _ = Group.objects.get_or_create(name="admin")
        admin_group.user_set.add(user)
        admin_group.save()

    groups = [model_to_dict(group) for group in user.groups.all().iterator()]
    return Response(groups)
