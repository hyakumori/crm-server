from rest_framework import permissions
from hyakumori_crm.permissions.enums import SystemGroups


def is_admin_request(request):
    return request.user.is_superuser or request.user.member_of(SystemGroups.GROUP_ADMIN)


class IsAdminUser(permissions.IsAuthenticated):
    """
    Allows access only to admin users or admin group
    """

    def has_permission(self, request, view):
        return (not request.user.is_anonymous) and is_admin_request(request)


class CurrentUserOrAdmin(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return is_admin_request(request) or obj.pk == request.user.pk
