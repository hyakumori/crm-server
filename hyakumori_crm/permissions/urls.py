from django.urls import path

from .views import (
    get_user_permissions,
    get_resource_permissions,
    assign_user_resource_permissions,
    add_user_group,
    setup_groups,
    remove_user_group,
)

api_urls = [
    path("permissions/user", get_user_permissions, name="list-user-permissions"),
    path(
        "permissions/assign",
        assign_user_resource_permissions,
        name="assign-permissions",
    ),
    path(
        "permissions/unassign",
        assign_user_resource_permissions,
        name="assign-permissions",
    ),
    path("permissions/add-group", add_user_group, name="add-user-group"),
    path("permissions/remove-group", remove_user_group, name="remove-user-group"),
    path("permissions/setup-groups", setup_groups, name="setup-groups"),
    path("permissions", get_resource_permissions, name="list-permissions"),
]
