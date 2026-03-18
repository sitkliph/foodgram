from rest_framework import permissions


class IsAuthorOrAdmin(permissions.BasePermission):
    """Разрешение для доступа авторам или администраторам."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                obj.author == request.user
                or request.user.is_staff
            )
        )
