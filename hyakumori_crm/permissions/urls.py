from django.urls import path

from .views import get_resource_permissions, get_groups

api_urls = [
    path("permissions", get_resource_permissions, name="list-permissions"),
    path("permissions/groups", get_groups, name="list-groups"),
]
