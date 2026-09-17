from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    message = "Admin access only"

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_admin_role)


class IsDonorOrAdmin(BasePermission):
    message = "Only donors can donate food"

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.role == user.Role.DONOR or user.is_admin_role))
