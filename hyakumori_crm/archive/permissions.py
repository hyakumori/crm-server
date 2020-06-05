from rest_framework.permissions import BasePermission


class ChangeArchivePersmission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perms(["crm.change_archive"])
