# =============================================================================
# apps/users/tasks.py
# =============================================================================
from django.tasks import task
from services.email import EmailService


@task()
def send_welcome_email(user_id: str, storefront_id: str = None):
    from apps.users.models import User
    from apps.storefronts.models import Storefront
    try:
        user = User.objects.get(id=user_id)
        storefront = Storefront.objects.filter(id=storefront_id).first() if storefront_id else None
        EmailService.send_welcome(user, storefront)
    except User.DoesNotExist:
        pass


@task()
def send_password_reset_email(user_id: str, reset_url: str, storefront_id: str = None):
    from apps.users.models import User
    from apps.storefronts.models import Storefront
    try:
        user = User.objects.get(id=user_id)
        storefront = Storefront.objects.filter(id=storefront_id).first() if storefront_id else None
        EmailService.send_password_reset(user, reset_url, storefront)
    except User.DoesNotExist:
        pass
