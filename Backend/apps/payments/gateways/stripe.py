
# =============================================================================
# apps/payments/gateways/stripe.py
# =============================================================================
import logging
from decimal import Decimal
from django.conf import settings
from .base import BaseGateway, PaymentIntent, ChargeResult, RefundResult

logger = logging.getLogger(__name__)


class StripeGateway(BaseGateway):
    """
    Stripe integration using stripe-python SDK.
    Requires settings:
        STRIPE_SECRET_KEY
        STRIPE_WEBHOOK_SECRET
    """

    def __init__(self):
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self._stripe   = stripe

    # ------------------------------------------------------------------
    # Interface implementation
    # ------------------------------------------------------------------

    def create_payment_intent(self, order) -> PaymentIntent:
        """
        Creates a Stripe PaymentIntent.
        The frontend uses the returned client_secret with Stripe.js
        to complete the payment without sensitive data touching your server.
        """
        try:
            amount_cents = int(order.total * 100)   # Stripe works in pence/cents
            intent = self._stripe.PaymentIntent.create(
                amount   = amount_cents,
                currency = "usd",
                metadata = {
                    "order_id": str(order.id),
                    "user_id":  str(order.user.id),
                },
                # Automatically confirm when the frontend provides payment method
                automatic_payment_methods = {"enabled": True},
            )
            logger.info("Stripe PaymentIntent created: %s for order %s", intent.id, order.id)
            return PaymentIntent(
                gateway_ref   = intent.id,
                client_secret = intent.client_secret,
                approval_url  = None,
                amount        = order.total,
                currency      = "USD",
                status        = intent.status,
                raw           = dict(intent),
            )
        except self._stripe.error.StripeError as e:
            logger.exception("Stripe create_payment_intent failed for order %s: %s", order.id, e)
            raise

    def capture(self, gateway_ref: str) -> ChargeResult:
        """
        Capture a PaymentIntent that was created with capture_method="manual".
        For automatic capture this is handled by Stripe itself after confirmation.
        """
        try:
            intent = self._stripe.PaymentIntent.capture(gateway_ref)
            return ChargeResult(
                gateway_ref = intent.id,
                amount      = Decimal(intent.amount_received) / 100,
                currency    = intent.currency.upper(),
                status      = "success" if intent.status == "succeeded" else "failed",
                raw         = dict(intent),
            )
        except self._stripe.error.StripeError as e:
            logger.exception("Stripe capture failed for %s: %s", gateway_ref, e)
            raise

    def refund(self, gateway_ref: str, amount: float) -> RefundResult:
        """
        Issues a partial or full refund.
        gateway_ref is the PaymentIntent ID — Stripe resolves the charge internally.
        """
        try:
            # Retrieve the charge ID from the intent first
            intent    = self._stripe.PaymentIntent.retrieve(gateway_ref)
            charge_id = intent.latest_charge

            refund = self._stripe.Refund.create(
                charge = charge_id,
                amount = int(amount * 100),
            )
            logger.info("Stripe refund %s issued for charge %s", refund.id, charge_id)
            return RefundResult(
                refund_ref = refund.id,
                amount     = Decimal(refund.amount) / 100,
                currency   = refund.currency.upper(),
                status     = "success" if refund.status == "succeeded" else "failed",
                raw        = dict(refund),
            )
        except self._stripe.error.StripeError as e:
            logger.exception("Stripe refund failed for %s: %s", gateway_ref, e)
            raise

    def retrieve(self, gateway_ref: str) -> dict:
        try:
            intent = self._stripe.PaymentIntent.retrieve(gateway_ref)
            return dict(intent)
        except self._stripe.error.StripeError as e:
            logger.exception("Stripe retrieve failed for %s: %s", gateway_ref, e)
            raise

    def cancel(self, gateway_ref: str) -> dict:
        try:
            intent = self._stripe.PaymentIntent.cancel(gateway_ref)
            return dict(intent)
        except self._stripe.error.StripeError as e:
            logger.exception("Stripe cancel failed for %s: %s", gateway_ref, e)
            raise

    # ------------------------------------------------------------------
    # Stripe-specific helpers (not part of BaseGateway)
    # ------------------------------------------------------------------

    def construct_webhook_event(self, payload: bytes, sig_header: str):
        """
        Verifies and constructs a Stripe webhook event.
        Called by StripeWebhookView before enqueueing handle_stripe_event.
        """
        return self._stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

    def get_payment_method(self, payment_method_id: str) -> dict:
        """Retrieves a saved payment method by ID."""
        return dict(self._stripe.PaymentMethod.retrieve(payment_method_id))

    def create_customer(self, user) -> str:
        """
        Creates a Stripe Customer for a user and returns the customer ID.
        Store this on the User model if you want to support saved cards.
        """
        customer = self._stripe.Customer.create(
            email    = user.email,
            name     = f"{user.first_name} {user.last_name}".strip(),
            metadata = {"user_id": str(user.id)},
        )
        return customer.id

