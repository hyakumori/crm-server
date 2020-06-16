from rest_framework.permissions import BasePermission


class CanChangePostalHistory(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perms(["crm.change_postal_history"])
