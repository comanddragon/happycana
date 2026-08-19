
# =============================================================================
# apps/notifications/admin.py
# =============================================================================
from django.contrib import admin
from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ["user", "type", "title", "is_read", "created_at"]
    list_filter   = ["type", "is_read", "created_at"]
    search_fields = ["user__email", "title"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["user"]

    actions = ["mark_as_read", "mark_as_unread"]

    @admin.action(description="Mark selected as read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Mark selected as unread")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)

