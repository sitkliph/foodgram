from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser

UserAdmin.fieldsets += (
    ('Дополнительная информация', {'fields': ('avatar',)}),
)
UserAdmin.search_fields = ('username', 'email')

admin.site.register(CustomUser, UserAdmin)
