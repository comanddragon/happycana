# =============================================================================
# apps/users/tasks.py
# =============================================================================
from django.tasks import task
from services.email import EmailService


@task()
def send_welcome_email(user_id: str):
    from apps.users.models import User
    try:
        user = User.objects.get(id=user_id)
        EmailService.send_welcome(user)
    except User.DoesNotExist:
        pass


@task()
def send_password_reset_email(user_id: str, reset_url: str):
    from apps.users.models import User
    try:
        user = User.objects.get(id=user_id)
        EmailService.send_password_reset(user, reset_url)
    except User.DoesNotExist:
        pass
