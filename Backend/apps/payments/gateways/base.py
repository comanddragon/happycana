# =============================================================================
# apps/payments/gateways/base.py
# Abstract interface every gateway must implement.
# PaymentService and tasks only ever interact with this interface —
# swapping or adding a gateway never touches anything outside this folder.
# =============================================================================
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class PaymentIntent:
    """
    Returned by create_payment_intent().
    Contains everything the frontend needs to complete the payment.
    """
    gateway_ref:   str           # e.g. Stripe's pi_xxx or PayPal's order ID
    client_secret: Optional[str] # Stripe client secret for frontend SDK
    approval_url:  Optional[str] # PayPal redirect URL
    amount:        Decimal
    currency:      str
    status:        str           # "requires_payment_method" | "created" | etc.
    raw:           dict          # full raw response from the gateway


@dataclass
class ChargeResult:
    """Returned by capture() and charge()."""
    gateway_ref: str
    amount:      Decimal
    currency:    str
    status:      str             # "success" | "failed" | "pending"
    raw:         dict


@dataclass
class RefundResult:
    """Returned by refund()."""
    refund_ref:  str
    amount:      Decimal
    currency:    str
    status:      str             # "success" | "failed" | "pending"
    raw:         dict


class BaseGateway(ABC):

    @abstractmethod
    def create_payment_intent(self, order) -> PaymentIntent:
        """
        Initialise a payment with the gateway and return a PaymentIntent.
        For Stripe this creates a PaymentIntent.
        For PayPal this creates an Order and returns an approval URL.
        """

    @abstractmethod
    def capture(self, gateway_ref: str) -> ChargeResult:
        """
        Capture a previously authorised payment.
        Called after the frontend confirms the payment.
        """

    @abstractmethod
    def refund(self, gateway_ref: str, amount: float) -> RefundResult:
        """Issue a full or partial refund against a captured charge."""

    @abstractmethod
    def retrieve(self, gateway_ref: str) -> dict:
        """Fetch the current state of a payment from the gateway."""

    @abstractmethod
    def cancel(self, gateway_ref: str) -> dict:
        """Cancel an uncaptured payment intent or authorisation."""
