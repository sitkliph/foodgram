from django.contrib.auth.models import AbstractUser
from django.db import models

from backend.constants import USER_CHAR_FIELDS_LENGTH


class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя.

    Добавлено поле avatar, заменено поле для аутентификации и добавлены
    обязательные поля first_name и last_name при регистрации для работы Djoser
    согласно спецификации.
    """

    email = models.EmailField(unique=True)
    first_name = models.CharField('Имя', max_length=USER_CHAR_FIELDS_LENGTH)
    last_name = models.CharField('Фамилия', max_length=USER_CHAR_FIELDS_LENGTH)
    avatar = models.ImageField(
        'Аватар', upload_to='users/', blank=True, null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username', ]


class Subscription(models.Model):
    """Модель, хранящая информация о подкисках пользователей."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]
