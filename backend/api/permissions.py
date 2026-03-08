from rest_framework import permissions


class DenyAll(permissions.BasePermission):
    """Запрет доступа всем пользователям."""

    def has_permission(self, request, view):
        return False


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение для доступа авторам или администраторам, или доступа для чтения.

    При GET запросах: доступ разрешен всем пользователям.
    При POST запросах: доступ разрешен аутентифицированным пользователям.
    При PATCH, DELETE запросах: доступ разрешен только авторам объектам и
    администраторам.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                obj.author == request.user
                or request.user.is_staff
            )
        )
