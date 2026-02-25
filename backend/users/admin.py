from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser

UserAdmin.fieldsets += (
    ('Additional info', {'fields': ('avatar',)}),
)
UserAdmin.search_fields = ('username', 'email')

admin.site.register(CustomUser, UserAdmin)
