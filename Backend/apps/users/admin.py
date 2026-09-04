# =============================================================================
# apps/users/admin.py
# =============================================================================
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.users.models import User, Address


class AddressInline(admin.TabularInline):
    model  = Address
    extra  = 0
    fields = ["line1", "city", "country", "is_default"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines         = [AddressInline]
    list_display    = ["email", "first_name", "last_name", "is_active", "is_staff", "created_at"]
    list_filter     = ["is_active", "is_staff", "created_at"]
    search_fields   = ["email", "first_name", "last_name"]
    ordering        = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets       = (
        (None,           {"fields": ("email", "password")}),
        ("Personal info",{"fields": ("first_name", "last_name", "phone", "date_of_birth")}),
        ("Permissions",  {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Timestamps",   {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields":  ("email", "password1", "password2"),
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display  = ["user", "line1", "city", "country", "is_default"]
    list_filter   = ["country", "is_default"]
    search_fields = ["user__email", "line1", "city"]
    raw_id_fields = ["user"]
