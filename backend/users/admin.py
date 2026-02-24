from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser

UserAdmin.fieldsets += (
    ('Additional info', {'fields': ('avatar',)}),
)

admin.site.register(CustomUser, UserAdmin)
