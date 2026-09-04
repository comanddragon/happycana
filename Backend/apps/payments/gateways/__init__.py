# =============================================================================
# apps/payments/gateways/__init__.py
# =============================================================================
from .stripe import StripeGateway
from .paypal import PayPalGateway
from .base import BaseGateway


class GatewayFactory:
    """
    Resolves the correct gateway instance by name.
    Add new gateways here — nothing else needs to change.

    Usage:
        gateway = GatewayFactory.get("stripe")
        gateway = GatewayFactory.get("paypal")
    """
    _registry = {
        "stripe": StripeGateway,
        "paypal": PayPalGateway,
    }

    @classmethod
    def get(cls, name: str) -> BaseGateway:
        klass = cls._registry.get(name.lower())
        if not klass:
            raise ValueError(
                f"Unknown payment gateway '{name}'. "
                f"Available: {list(cls._registry.keys())}"
            )
        return klass()
