from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Storefront, StorefrontDomain, StorefrontOrigin


class StorefrontDomainInline(admin.TabularInline):
    model = StorefrontDomain
    extra = 0


class StorefrontOriginInline(admin.TabularInline):
    model = StorefrontOrigin
    extra = 0


@admin.register(Storefront)
class StorefrontAdmin(ModelAdmin):
    list_display = ("name", "slug", "kind", "currency", "from_email", "is_active")
    list_filter = ("kind", "is_active")
    search_fields = ("name", "slug")
    inlines = (StorefrontDomainInline, StorefrontOriginInline)
