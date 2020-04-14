from guardian.utils import AnonymousUser, get_identity
from rest_framework import permissions


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
        if hasattr(obj, 'author') and obj.author == request_user:
            return True

        return False

    def has_permission(self, request, view):
        if request.user and not request.user.is_anonymous:
            return True

        return False


class DisallowDeleteAnon(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['DELETE'] and isinstance(request.user, type(AnonymousUser)):
            return False

        return True
