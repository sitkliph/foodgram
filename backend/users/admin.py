from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User

UserAdmin.fieldsets += (
    ('Дополнительная информация', {'fields': ('avatar',)}),
)
UserAdmin.list_display += ('recipes', 'subscribers')
UserAdmin.search_fields = ('username', 'email')


@admin.display(description='Рецепты')
def recipes(self, obj):
    return obj.recipes.count()


@admin.display(description='Подписчики')
def subscribers(self, obj):
    return obj.subscribers.count()


UserAdmin.recipes = recipes
UserAdmin.subscribers = subscribers

admin.site.register(User, UserAdmin)
