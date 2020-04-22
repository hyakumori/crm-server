from django.urls import path

from .views import get_resource_permissions, setup_groups, get_groups

api_urls = [
    path("permissions/setup-groups", setup_groups, name="setup-groups"),
    path("permissions", get_resource_permissions, name="list-permissions"),
    path("permissions/groups", get_groups, name="list-groups"),
]
