
# =============================================================================
# apps/payments/gateways/paypal.py
# =============================================================================
import logging
import requests
from decimal import Decimal
from django.conf import settings
from .base import BaseGateway, PaymentIntent, ChargeResult, RefundResult

logger = logging.getLogger(__name__)


class PayPalGateway(BaseGateway):
    """
    PayPal REST API v2 integration (Orders API).
    Requires settings:
        PAYPAL_CLIENT_ID
        PAYPAL_CLIENT_SECRET
        PAYPAL_BASE_URL  e.g. https://api-m.sandbox.paypal.com (sandbox)
                              https://api-m.paypal.com          (production)
    """

    def __init__(self):
        self.base_url      = settings.PAYPAL_BASE_URL
        self.client_id     = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self._token        = None

    # ------------------------------------------------------------------
    # Interface implementation
    # ------------------------------------------------------------------

    def create_payment_intent(self, order) -> PaymentIntent:
        """
        Creates a PayPal Order and returns the approval URL.
        The frontend redirects the user to approval_url to authorise payment.
        After approval PayPal redirects back to your PAYPAL_RETURN_URL.
        """
        try:
            response = self._post("/v2/checkout/orders", {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "reference_id": str(order.id),
                    "amount": {
                        "currency_code": "USD",
                        "value": str(order.total),
                    },
                }],
                "application_context": {
                    "return_url": settings.PAYPAL_RETURN_URL,
                    "cancel_url": settings.PAYPAL_CANCEL_URL,
                },
            })
            approval_url = next(
                (link["href"] for link in response.get("links", []) if link["rel"] == "approve"),
                None,
            )
            logger.info("PayPal order created: %s for order %s", response["id"], order.id)
            return PaymentIntent(
                gateway_ref   = response["id"],
                client_secret = None,
                approval_url  = approval_url,
                amount        = order.total,
                currency      = "USD",
                status        = response["status"],
                raw           = response,
            )
        except Exception as e:
            logger.exception("PayPal create_payment_intent failed for order %s: %s", order.id, e)
            raise

    def capture(self, gateway_ref: str) -> ChargeResult:
        """
        Captures an approved PayPal order.
        Called after the user returns from the PayPal approval URL.
        """
        try:
            response = self._post(f"/v2/checkout/orders/{gateway_ref}/capture", {})
            unit     = response["purchase_units"][0]
            capture  = unit["payments"]["captures"][0]
            return ChargeResult(
                gateway_ref = capture["id"],
                amount      = Decimal(capture["amount"]["value"]),
                currency    = capture["amount"]["currency_code"],
                status      = "success" if capture["status"] == "COMPLETED" else "failed",
                raw         = response,
            )
        except Exception as e:
            logger.exception("PayPal capture failed for %s: %s", gateway_ref, e)
            raise

    def refund(self, gateway_ref: str, amount: float) -> RefundResult:
        """
        Issues a refund against a PayPal capture ID.
        gateway_ref here should be the capture ID, not the order ID.
        """
        try:
            response = self._post(f"/v2/payments/captures/{gateway_ref}/refund", {
                "amount": {
                    "value":         f"{amount:.2f}",
                    "currency_code": "USD",
                },
            })
            logger.info("PayPal refund %s issued for capture %s", response["id"], gateway_ref)
            return RefundResult(
                refund_ref = response["id"],
                amount     = Decimal(response["amount"]["value"]),
                currency   = response["amount"]["currency_code"],
                status     = "success" if response["status"] == "COMPLETED" else "pending",
                raw        = response,
            )
        except Exception as e:
            logger.exception("PayPal refund failed for %s: %s", gateway_ref, e)
            raise

    def retrieve(self, gateway_ref: str) -> dict:
        try:
            return self._get(f"/v2/checkout/orders/{gateway_ref}")
        except Exception as e:
            logger.exception("PayPal retrieve failed for %s: %s", gateway_ref, e)
            raise

    def cancel(self, gateway_ref: str) -> dict:
        """
        PayPal orders in CREATED or APPROVED status can simply be abandoned —
        there is no explicit cancel endpoint for Orders API v2.
        For authorised payments use /v2/payments/authorizations/{id}/void.
        """
        try:
            order = self.retrieve(gateway_ref)
            if order.get("status") == "APPROVED":
                return self._post(
                    f"/v2/payments/authorizations/{gateway_ref}/void", {}
                )
            return order
        except Exception as e:
            logger.exception("PayPal cancel failed for %s: %s", gateway_ref, e)
            raise

    # ------------------------------------------------------------------
    # PayPal-specific helpers
    # ------------------------------------------------------------------

    def handle_webhook(self, headers: dict, body: dict) -> dict:
        """
        Verifies and returns a PayPal webhook event.
        Called by a PayPalWebhookView (add to payments/api/views.py).
        """
        verified = self._post("/v1/notifications/verify-webhook-signature", {
            "auth_algo":         headers.get("PAYPAL-AUTH-ALGO"),
            "cert_url":          headers.get("PAYPAL-CERT-URL"),
            "transmission_id":   headers.get("PAYPAL-TRANSMISSION-ID"),
            "transmission_sig":  headers.get("PAYPAL-TRANSMISSION-SIG"),
            "transmission_time": headers.get("PAYPAL-TRANSMISSION-TIME"),
            "webhook_id":        settings.PAYPAL_WEBHOOK_ID,
            "webhook_event":     body,
        })
        if verified.get("verification_status") != "SUCCESS":
            raise ValueError("PayPal webhook signature verification failed.")
        return body

    # ------------------------------------------------------------------
    # HTTP helpers — token auth + JSON requests
    # ------------------------------------------------------------------

    def _get_access_token(self) -> str:
        if self._token:
            return self._token
        response = requests.post(
            f"{self.base_url}/v1/oauth2/token",
            auth    = (self.client_id, self.client_secret),
            data    = {"grant_type": "client_credentials"},
            timeout = 10,
        )
        response.raise_for_status()
        self._token = response.json()["access_token"]
        return self._token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type":  "application/json",
        }

    def _post(self, path: str, payload: dict) -> dict:
        response = requests.post(
            f"{self.base_url}{path}",
            json    = payload,
            headers = self._headers(),
            timeout = 15,
        )
        response.raise_for_status()
        return response.json() if response.content else {}

    def _get(self, path: str) -> dict:
        response = requests.get(
            f"{self.base_url}{path}",
            headers = self._headers(),
            timeout = 10,
        )
        response.raise_for_status()
        return response.json()
