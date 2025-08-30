from rest_framework import permissions

class CanExportBills(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (
            request.user.is_superuser or request.user.has_perm('core.can_export_bills')
        ))
