from rest_framework.permissions import BasePermission


class DenyAll(BasePermission):
    """Запрет доступа всем пользователям."""

    def has_permission(self, request, view):
        return False
