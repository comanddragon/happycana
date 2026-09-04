import uuid
from django.db import models
from apps.users.models import User
from .mangers import NotificationManager

class Notification(models.Model):
    class Type(models.TextChoices):
        ORDER      = "order",      "Order Update"
        PAYMENT    = "payment",    "Payment"
        SHIPMENT   = "shipment",   "Shipment"
        PROMOTION  = "promotion",  "Promotion"
        SYSTEM     = "system",     "System"

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    type       = models.CharField(max_length=20, choices=Type.choices)
    title      = models.CharField(max_length=255)
    body       = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = NotificationManager()

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.type}: {self.title} → {self.user.email}"