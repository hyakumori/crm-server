from rest_framework.permissions import BasePermission
from hyakumori_crm.users.backends import HyakumoriBackend


class DownloadCsvPersmission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perms(["crm.view_customer"])


class CustomerContactListPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("crm.view_customer") or request.user.has_perm(
            "crm.manage_archive"
        )
