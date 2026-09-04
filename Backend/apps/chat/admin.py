# =============================================================================
# apps/chat/admin.py
# =============================================================================
from django.contrib import admin
from apps.chat.models import ChatRoom, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model           = ChatMessage
    extra           = 0
    readonly_fields = ["sender", "message_type", "body", "is_read", "created_at"]
    can_delete      = False
    ordering        = ["created_at"]


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    inlines         = [ChatMessageInline]
    list_display    = ["id", "customer", "agent", "subject", "status", "created_at", "updated_at"]
    list_filter     = ["status", "created_at"]
    search_fields   = ["customer__email", "agent__email", "subject"]
    readonly_fields = ["id", "created_at", "updated_at"]
    raw_id_fields   = ["customer", "agent", "order"]
    actions         = ["mark_resolved", "mark_closed"]

    @admin.action(description="Mark selected rooms as Resolved")
    def mark_resolved(self, request, queryset):
        queryset.update(status=ChatRoom.Status.RESOLVED)

    @admin.action(description="Mark selected rooms as Closed")
    def mark_closed(self, request, queryset):
        queryset.update(status=ChatRoom.Status.CLOSED)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display    = ["id", "room", "sender", "message_type", "body_preview", "is_read", "created_at"]
    list_filter     = ["message_type", "is_read", "created_at"]
    search_fields   = ["sender__email", "body"]
    readonly_fields = ["id", "created_at"]
    raw_id_fields   = ["room", "sender"]

    @admin.display(description="Body")
    def body_preview(self, obj):
        return obj.body[:80] + ("…" if len(obj.body) > 80 else "")
