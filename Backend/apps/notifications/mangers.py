
# =============================================================================
# apps/notifications/managers.py
# =============================================================================
from django.db import models as db_models


class NotificationQuerySet(db_models.QuerySet):

    def for_user(self, user):
        return self.filter(user=user)

    def unread(self):
        return self.filter(is_read=False)

    def read(self):
        return self.filter(is_read=True)

    def by_type(self, notification_type):
        return self.filter(type=notification_type)

    def older_than(self, days):
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__lt=cutoff)


class NotificationManager(db_models.Manager):
    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user)

    def unread_for_user(self, user):
        return self.get_queryset().for_user(user).unread()

    def cleanup_old(self, days=30):
        """Used by notifications.tasks.cleanup_old_notifications."""
        return self.get_queryset().read().older_than(days)


# Integrate into apps/notifications/models.py:
#   Notification.objects = NotificationManager()
