
# =============================================================================
# apps/notifications/signals.py  — Fires notification WS broadcast
# =============================================================================
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.notifications.models import Notification


@receiver(post_save, sender=Notification)
def broadcast_notification(sender, instance, created, **kwargs):
    if not created:
        return
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{instance.user_id}_notifications",
        {
            "type":    "notification_new",
            "payload": {
                "id":         str(instance.id),
                "type":       instance.type,
                "title":      instance.title,
                "body":       instance.body,
                "created_at": instance.created_at.isoformat(),
            },
        }
    )