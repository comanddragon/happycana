# =============================================================================
# services/email.py
# Thin abstraction over Django's email backend.
# Swap the backend in settings without touching call sites.
# =============================================================================
from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:

    FROM = settings.DEFAULT_FROM_EMAIL

    @classmethod
    def send(cls, subject, body, recipients, html_body=None):
        """Send a plain-text (optionally HTML) email to one or more recipients."""
        try:
            if html_body:
                msg = EmailMultiAlternatives(subject, body, cls.FROM, recipients)
                msg.attach_alternative(html_body, "text/html")
                msg.send()
            else:
                send_mail(subject, body, cls.FROM, recipients, fail_silently=False)
            logger.info("Email sent to %s — subject: %s", recipients, subject)
        except Exception as exc:
            logger.exception("Failed to send email to %s: %s", recipients, exc)
            raise

    @classmethod
    def send_template(cls, subject, template_name, context, recipients):
        """Render a Django template and send as HTML email."""
        html_body = render_to_string(template_name, context)
        text_body = render_to_string(
            template_name.replace(".html", ".txt"), context
        )
        cls.send(subject, text_body, recipients, html_body=html_body)

    # ------------------------------------------------------------------
    # Transactional helpers used across apps
    # ------------------------------------------------------------------

    @classmethod
    def send_welcome(cls, user):
        cls.send_template(
            subject       = "Welcome to the store!",
            template_name = "emails/welcome.html",
            context       = {"user": user},
            recipients    = [user.email],
        )

    @classmethod
    def send_order_confirmation(cls, order):
        cls.send_template(
            subject       = f"Order #{order.id} Confirmed",
            template_name = "emails/order_confirmation.html",
            context       = {"order": order, "items": order.items.all()},
            recipients    = [order.user.email],
        )

    @classmethod
    def send_order_shipped(cls, order, shipment):
        cls.send_template(
            subject       = f"Your order #{order.id} has shipped!",
            template_name = "emails/order_shipped.html",
            context       = {"order": order, "shipment": shipment},
            recipients    = [order.user.email],
        )

    @classmethod
    def send_password_reset(cls, user, reset_url):
        cls.send_template(
            subject       = "Reset your password",
            template_name = "emails/password_reset.html",
            context       = {"user": user, "reset_url": reset_url},
            recipients    = [user.email],
        )

    @classmethod
    def send_refund_processed(cls, refund):
        cls.send_template(
            subject       = "Refund Processed",
            template_name = "emails/refund_processed.html",
            context       = {"refund": refund},
            recipients    = [refund.payment.order.user.email],
        )

