from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Shaxsiy ma'lumotlar", {"fields": ("first_name", "last_name")}),
        ("Rol", {"fields": ("role",)}),
        ("Ruxsatlar", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "password1", "password2", "first_name", "last_name", "role"),
        }),
    )
    list_display = ("phone_number", "first_name", "last_name", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_active")
    ordering = ("phone_number",)
    search_fields = ("phone_number", "first_name", "last_name")
    filter_horizontal = ()
