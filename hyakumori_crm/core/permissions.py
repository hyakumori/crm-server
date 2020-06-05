from guardian.utils import AnonymousUser, get_identity
from rest_framework import permissions

from ..permissions.enums import SystemGroups


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user


class IsStaffOrListOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True

        if (request.query_params.get("pk") is None) and (request.method == "GET"):
            return True

        return False


class IsAdminOrSelf(permissions.BasePermission):
    """
    Allow access to admin users or the user himself.
    Apply to model with object with `author` field or current user object
    """

    def has_object_permission(self, request, view, obj):
        request_user = get_identity(request.user)[0]

        if request_user and request_user.is_staff:
            return True

        user_type = type(request_user)

        # current checking resource object is user
        # allow user see himself
        if isinstance(obj, user_type) and obj == request.user:
            return True

        # current object has `author` field
        if hasattr(obj, "author") and obj.author == request_user:
            return True

        return False

    def has_permission(self, request, view):
        if request.user and not request.user.is_anonymous:
            return True

        return False


class DisallowDeleteAnon(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ["DELETE"] and isinstance(
            request.user, type(AnonymousUser)
        ):
            return False

        return True


class AdminGroupPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.member_of(SystemGroups.GROUP_ADMIN)


class ModelPermissions(permissions.DjangoModelPermissions):
    model_cls = None

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

    def has_permission(self, request, view):
        if getattr(view, "_ignore_model_permissions", False):
            return True

        if not request.user or (
            not request.user.is_authenticated and self.authenticated_users_only
        ):
            return False

        perms = self.get_required_permissions(request.method, self.model_cls)
        return request.user.has_perms(perms)
