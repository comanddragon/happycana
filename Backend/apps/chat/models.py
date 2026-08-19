# =============================================================================
# apps/chat/models.py
# =============================================================================
import uuid
from django.db import models
from apps.users.models import User


class ChatRoom(models.Model):
    """
    A chat room between a customer and support agent.
    Can be tied to an order (for order-related support) or standalone.
    """
    class Status(models.TextChoices):
        OPEN       = "open",       "Open"
        ASSIGNED   = "assigned",   "Assigned"
        RESOLVED   = "resolved",   "Resolved"
        CLOSED     = "closed",     "Closed"

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_rooms")
    agent      = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_chats"
    )
    order      = models.ForeignKey(
        "orders.Order", on_delete=models.SET_NULL, null=True, blank=True, related_name="chat_rooms"
    )
    subject    = models.CharField(max_length=255, blank=True)
    status     = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "chat_rooms"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Room {self.id} — {self.customer.email} [{self.status}]"

    @property
    def group_name(self):
        return f"chat_{self.id}"


class ChatMessage(models.Model):
    """Persisted chat message within a ChatRoom."""

    class MessageType(models.TextChoices):
        TEXT   = "text",   "Text"
        IMAGE  = "image",  "Image"
        FILE   = "file",   "File"
        SYSTEM = "system", "System"   # e.g. "Agent joined", "Room resolved"

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room       = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender     = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="chat_messages"
    )
    message_type = models.CharField(max_length=10, choices=MessageType.choices, default=MessageType.TEXT)
    body       = models.TextField()
    file       = models.FileField(upload_to="chat/files/", blank=True, null=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_messages"
        ordering = ["created_at"]

    def __str__(self):
        sender = self.sender.email if self.sender else "System"
        return f"[{sender}] {self.body[:60]}"