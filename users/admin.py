from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from .models import User


class UserAdmin(auth_admin.UserAdmin):
    list_display = ("username", "email", "full_name", "is_staff")
    fieldsets = auth_admin.UserAdmin.fieldsets + (
        ("Custom Profile", {"fields": ("full_name", "bio", "avatar")}),
    )

admin.site.register(User, UserAdmin)