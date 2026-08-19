
# =============================================================================
# services/sms.py
# SMS abstraction via Twilio. Swap provider without touching call sites.
# =============================================================================
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class SMSService:

    @staticmethod
    def _get_client():
        from twilio.rest import Client
        return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    @classmethod
    def send(cls, to, body):
        """Send a raw SMS to a phone number in E.164 format e.g. +1234567890."""
        try:
            client = cls._get_client()
            message = client.messages.create(
                body = body,
                from_= settings.TWILIO_FROM_NUMBER,
                to   = to,
            )
            logger.info("SMS sent to %s — SID: %s", to, message.sid)
            return message.sid
        except Exception as exc:
            logger.exception("Failed to send SMS to %s: %s", to, exc)
            raise

    # ------------------------------------------------------------------
    # Transactional helpers
    # ------------------------------------------------------------------

    @classmethod
    def send_order_shipped(cls, order, tracking_number):
        if not order.user.phone:
            return
        cls.send(
            to   = order.user.phone,
            body = (
                f"Your order #{str(order.id)[:8]} has shipped! "
                f"Track it with: {tracking_number}"
            ),
        )

    @classmethod
    def send_otp(cls, phone, otp_code):
        cls.send(
            to   = phone,
            body = f"Your verification code is: {otp_code}. It expires in 10 minutes.",
        )

    @classmethod
    def send_delivery_confirmation(cls, order):
        if not order.user.phone:
            return
        cls.send(
            to   = order.user.phone,
            body = f"Your order #{str(order.id)[:8]} has been delivered. Thank you for shopping with us!",
        )

