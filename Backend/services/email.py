# =============================================================================
# services/email.py
# Thin abstraction over Resend — swap providers in one place without
# touching call sites.
# =============================================================================
from django.template.loader import render_to_string
from django.conf import settings
import logging
import resend

logger = logging.getLogger(__name__)

resend.api_key = settings.RESEND_API_KEY


class EmailService:

    FROM = settings.DEFAULT_FROM_EMAIL

    @classmethod
    def send(cls, subject, body, recipients, html_body=None):
        """Send a plain-text (optionally HTML) email to one or more recipients via Resend."""
        payload = {
            "from": cls.FROM,
            "to": recipients,
            "subject": subject,
            "text": body,
        }
        if html_body:
            payload["html"] = html_body
        try:
            result = resend.Emails.send(payload)
            email_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", None)
            logger.info(
                "Email sent to %s — subject: %s — resend id: %s",
                recipients, subject, email_id,
            )
        except Exception as exc:
            logger.exception("Failed to send email to %s: %s", recipients, exc)
            raise

    @classmethod
    def send_template(cls, subject, template_name, context, recipients):
        """Render a Django template and send as HTML email."""
        context = {**cls._base_context(), **context}
        html_body = render_to_string(template_name, context)
        text_body = render_to_string(
            template_name.replace(".html", ".txt"), context
        )
        cls.send(subject, text_body, recipients, html_body=html_body)

    @classmethod
    def _base_context(cls):
        """Branding vars used by every templates/emails/*.html template."""
        return {
            "store_name": settings.STORE_NAME,
            "store_url": settings.FRONTEND_URL,
            "logo_url": settings.STORE_LOGO_URL,
            "support_email": settings.SUPPORT_EMAIL,
            "store_address": settings.STORE_ADDRESS,
            "unsubscribe_url": f"{settings.FRONTEND_URL}/account/notifications",
        }

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
    def send_order_placed(cls, order):
        """Sent immediately at checkout — a receipt of what was ordered.
        Distinct from send_order_confirmation, which fires once payment is
        actually confirmed."""
        cls.send_template(
            subject       = f"We've received your order #{order.short_id}",
            template_name = "emails/order_placed.html",
            context       = {"order": order, "items": order.items.all()},
            recipients    = [order.user.email],
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
    def send_order_delivered(cls, order, shipment=None):
        cls.send_template(
            subject       = f"Order #{order.id} has been delivered",
            template_name = "emails/order_delivered.html",
            context       = {"order": order, "shipment": shipment},
            recipients    = [order.user.email],
        )

    @classmethod
    def send_payment_confirmation(cls, payment):
        """Manually triggered by an admin once a payment is confirmed."""
        cls.send_template(
            subject       = f"Payment received for order #{payment.order.id}",
            template_name = "emails/payment_confirmation.html",
            context       = {"payment": payment},
            recipients    = [payment.order.user.email],
        )

    @classmethod
    def send_coupon(cls, coupon, recipients):
        cls.send_template(
            subject       = f"Save with code {coupon.code}",
            template_name = "emails/coupon.html",
            context       = {"coupon": coupon},
            recipients    = recipients,
        )

    @classmethod
    def send_refund_processed(cls, refund):
        cls.send_template(
            subject       = "Refund Processed",
            template_name = "emails/refund_processed.html",
            context       = {"refund": refund},
            recipients    = [refund.payment.order.user.email],
        )

    # ------------------------------------------------------------------
    # Order-placed admin notification
    # ------------------------------------------------------------------

    @classmethod
    def send_order_notification_to_admin(cls, order):
        """Notifies the store owner that an order was placed, so they can follow up manually about payment."""
        admin_email = settings.ADMIN_NOTIFICATION_EMAIL
        if not admin_email:
            logger.warning(
                "Skipping order notification for %s — ADMIN_NOTIFICATION_EMAIL is not configured.",
                order.id,
            )
            return

        cls.send_template(
            subject       = f"New order #{order.short_id} — ${order.total}",
            template_name = "emails/order_notification_admin.html",
            context       = {"order": order, "items": order.items.select_related("variant").all()},
            recipients    = [admin_email],
        )