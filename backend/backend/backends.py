from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class UsernameLoginBackend(ModelBackend):
    """Бэкэнд аутентификации по полю username модели пользователя."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        login = username
        if not login or not password:
            return None
        try:
            user = User.objects.get(username=login)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
