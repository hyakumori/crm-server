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


class IsAdminOrReadOnly(permissions.IsAuthenticated):
    """
    Allow authenticated for GET, HEAD, OPTIONS
    Allow `is_superuser`, `group_admin` for unsafe methods
    """
    def has_permission(self, request, view):
        is_authenticated = bool(request.user and request.user.is_authenticated)

        if not is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return is_admin_request(request)


class CurrentUserOrAdmin(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return is_admin_request(request) or obj.pk == request.user.pk
