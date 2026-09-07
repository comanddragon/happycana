# =============================================================================
# services/email.py
# Thin abstraction over Resend — swap providers in one place without
# touching call sites.
# =============================================================================
import base64
import logging
from functools import lru_cache
from pathlib import PurePosixPath
from urllib.parse import urlparse

import requests
import resend
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

resend.api_key = settings.RESEND_API_KEY


class EmailService:

    LOGO_CONTENT_ID = "store-logo"

    @staticmethod
    @lru_cache(maxsize=32)
    def _download_logo(logo_url):
        """Fetch and cache a logo so Resend receives the actual image content."""
        response = requests.get(logo_url, timeout=10)
        response.raise_for_status()
        return (
            base64.b64encode(response.content).decode("ascii"),
            response.headers.get("Content-Type", "image/png").split(";", 1)[0],
        )

    @classmethod
    def send(
        cls,
        subject,
        body,
        recipients,
        html_body=None,
        from_email=None,
        attachments=None,
    ):
        """Send a plain-text (optionally HTML) email to one or more recipients via Resend."""
        payload = {
            "from": from_email or settings.DEFAULT_FROM_EMAIL,
            "to": recipients,
            "subject": subject,
            "text": body,
        }
        if html_body:
            payload["html"] = html_body
        if attachments:
            payload["attachments"] = attachments
        try:
            result = resend.Emails.send(payload)
            email_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", None)
            logger.info(
                "Email sent to %s — subject: %s — resend id: %s",
                recipients, subject, email_id,
            )
        except Exception:
            logger.exception("Failed to send email to %s", recipients)
            raise

    @classmethod
    def send_template(cls, subject, template_name, context, recipients, storefront=None):
        """Render a Django template and send as HTML email."""
        context = {**cls._base_context(storefront), **context}
        logo_url = context.get("logo_url")
        attachments = None
        if logo_url:
            filename = PurePosixPath(urlparse(logo_url).path).name or "store-logo.png"
            try:
                logo_content, content_type = cls._download_logo(logo_url)
            except requests.RequestException:
                logger.warning("Could not embed email logo from %s", logo_url, exc_info=True)
            else:
                context["logo_url"] = f"cid:{cls.LOGO_CONTENT_ID}"
                attachments = [
                    {
                        "content": logo_content,
                        "filename": filename,
                        "content_type": content_type,
                        "content_id": cls.LOGO_CONTENT_ID,
                    }
                ]
        html_body = render_to_string(template_name, context)
        text_body = render_to_string(
            template_name.replace(".html", ".txt"), context
        )
        from_email = storefront.from_email if storefront and storefront.from_email else None
        cls.send(
            subject,
            text_body,
            recipients,
            html_body=html_body,
            from_email=from_email,
            attachments=attachments,
        )

    @classmethod
    def _base_context(cls, storefront=None):
        """Branding vars used by every templates/emails/*.html template."""
        store_url = storefront.frontend_url if storefront and storefront.frontend_url else settings.FRONTEND_URL
        return {
            "store_name": storefront.name if storefront else settings.STORE_NAME,
            "store_url": store_url,
            "backend_url": settings.BACKEND_URL.rstrip("/"),
            "logo_url": storefront.logo_url if storefront and storefront.logo_url else settings.STORE_LOGO_URL,
            "support_email": storefront.support_email if storefront and storefront.support_email else settings.SUPPORT_EMAIL,
            "store_address": storefront.postal_address if storefront and storefront.postal_address else settings.STORE_ADDRESS,
            "currency": storefront.currency if storefront else "USD",
            "unsubscribe_url": f"{store_url.rstrip('/')}/account/notifications",
        }

    # ------------------------------------------------------------------
    # Transactional helpers used across apps
    # ------------------------------------------------------------------

    @classmethod
    def send_welcome(cls, user, storefront=None):
        cls.send_template(
            subject       = "Welcome to the store!",
            template_name = "emails/welcome.html",
            context       = {"user": user},
            recipients    = [user.email],
            storefront    = storefront,
        )

    @classmethod
    def send_order_placed(cls, order):
        """Sent immediately at checkout — a receipt of what was ordered.
        Distinct from send_order_confirmation, which fires once payment is
        actually confirmed.
        """
        cls.send_template(
            subject       = f"We've received your order #{order.short_id}",
            template_name = "emails/order_placed.html",
            context       = {"order": order, "items": order.items.all()},
            recipients    = [order.user.email],
            storefront    = order.storefront,
        )

    @classmethod
    def send_order_confirmation(cls, order):
        cls.send_template(
            subject       = f"Order #{order.id} Confirmed",
            template_name = "emails/order_confirmation.html",
            context       = {"order": order, "items": order.items.all()},
            recipients    = [order.user.email],
            storefront    = order.storefront,
        )

    @classmethod
    def send_order_shipped(cls, order, shipment):
        cls.send_template(
            subject       = f"Your order #{order.id} has shipped!",
            template_name = "emails/order_shipped.html",
            context       = {"order": order, "shipment": shipment},
            recipients    = [order.user.email],
            storefront    = order.storefront,
        )

    @classmethod
    def send_password_reset(cls, user, reset_url, storefront=None):
        cls.send_template(
            subject       = "Reset your password",
            template_name = "emails/password_reset.html",
            context       = {"user": user, "reset_url": reset_url},
            recipients    = [user.email],
            storefront    = storefront,
        )

    @classmethod
    def send_order_delivered(cls, order, shipment=None):
        cls.send_template(
            subject       = f"Order #{order.id} has been delivered",
            template_name = "emails/order_delivered.html",
            context       = {"order": order, "shipment": shipment},
            recipients    = [order.user.email],
            storefront    = order.storefront,
        )

    @classmethod
    def send_payment_confirmation(cls, payment):
        """Manually triggered by an admin once a payment is confirmed."""
        cls.send_template(
            subject       = f"Payment received for order #{payment.order.id}",
            template_name = "emails/payment_confirmation.html",
            context       = {"payment": payment},
            recipients    = [payment.order.user.email],
            storefront    = payment.order.storefront,
        )

    @classmethod
    def send_coupon(cls, coupon, recipients):
        cls.send_template(
            subject       = f"Save with code {coupon.code}",
            template_name = "emails/coupon.html",
            context       = {"coupon": coupon},
            recipients    = recipients,
            storefront    = coupon.storefront,
        )

    @classmethod
    def send_refund_processed(cls, refund):
        cls.send_template(
            subject       = "Refund Processed",
            template_name = "emails/refund_processed.html",
            context       = {"refund": refund},
            recipients    = [refund.payment.order.user.email],
            storefront    = refund.payment.order.storefront,
        )

    # ------------------------------------------------------------------
    # Order-placed admin notification
    # ------------------------------------------------------------------

    @classmethod
    def send_order_notification_to_admin(cls, order):
        """Notifies the store owner that an order was placed, so they can follow up manually about payment."""
        storefront = order.storefront
        admin_email = (
            storefront.order_notification_email
            if storefront and storefront.order_notification_email
            else settings.ADMIN_NOTIFICATION_EMAIL
        )
        if not admin_email:
            logger.warning(
                "Skipping order notification for %s — ADMIN_NOTIFICATION_EMAIL is not configured.",
                order.id,
            )
            return

        cls.send_template(
            subject       = f"New order #{order.short_id} — {(storefront.currency if storefront else 'USD')} {order.total}",
            template_name = "emails/order_notification_admin.html",
            context       = {"order": order, "items": order.items.select_related("variant").all()},
            recipients    = [admin_email],
            storefront    = storefront,
        )
