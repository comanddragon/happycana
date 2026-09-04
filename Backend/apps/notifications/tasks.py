
# =============================================================================
# apps/notifications/tasks.py
# =============================================================================
from django.tasks import task


@task()
def send_push_notification(user_id: str, title: str, body: str):
    """
    Sends a push notification via FCM (Firebase Cloud Messaging).
    Extend with your FCM credentials and device token model.
    """
    import logging
    logger = logging.getLogger(__name__)

    from apps.users.models import User
    try:
        user = User.objects.get(id=user_id)
        # Placeholder — plug in your FCM / APNs integration here
        logger.info("Push notification sent to user %s: %s", user.email, title)
    except User.DoesNotExist:
        pass


@task()
def cleanup_old_notifications():
    """
    Deletes read notifications older than 30 days.
    Run nightly via cron to keep the notifications table lean.
    """
    from apps.notifications.models import Notification

    deleted, _ = Notification.objects.cleanup_old(days=30).delete()

    import logging
    logging.getLogger(__name__).info("Cleaned up %d old notifications.", deleted)
