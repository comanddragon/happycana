# =============================================================================
# apps/promotions/engine.py
# Single source of truth for all discount calculation logic.
# Used by CheckoutService, the coupon validation serializer, and the API.
# =============================================================================
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field
from typing import Optional
from django.utils import timezone
from apps.promotions.models import Coupon


class PromotionError(Exception):
    pass


@dataclass
class CartContext:
    """
    Snapshot of the cart passed into the engine.
    Decoupled from the ORM so the engine is fully unit-testable
    without hitting the database.
    """

    subtotal: Decimal
    item_count: int
    user_id: Optional[str] = None
    item_skus: list = field(default_factory=list)


@dataclass
class DiscountResult:
    coupon: Optional[Coupon]
    discount_amount: Decimal
    discount_type: str  # "percentage" | "fixed" | "none"
    applied_value: Decimal  # the raw coupon value before capping
    final_total: Decimal
    summary: str  # human-readable description e.g. "10% off → -$12.50"


class PromotionEngine:
    """
    Evaluates coupons against a CartContext and returns a DiscountResult.

    Usage:
        context = CartContext(subtotal=Decimal("125.00"), item_count=3)
        result  = PromotionEngine.apply_coupon("SAVE10", context)
        print(result.discount_amount)   # Decimal("12.50")
    """

    @classmethod
    def apply_coupon(
        cls, code: str, context: CartContext, storefront=None
    ) -> DiscountResult:
        coupon = cls._resolve(code, storefront)
        cls._validate(coupon, context)
        return cls._calculate(coupon, context)

    @classmethod
    def preview_coupon(
        cls, code: str, context: CartContext, storefront=None
    ) -> DiscountResult:
        """
        Same as apply_coupon but does NOT raise on validation failure —
        returns a zero-discount result with an error summary instead.
        Safe to call from the frontend for live coupon previews.
        """
        try:
            return cls.apply_coupon(code, context, storefront=storefront)
        except PromotionError as e:
            return DiscountResult(
                coupon=None,
                discount_amount=Decimal("0.00"),
                discount_type="none",
                applied_value=Decimal("0.00"),
                final_total=context.subtotal,
                summary=str(e),
            )

    @classmethod
    def calculate_without_coupon(cls, context: CartContext) -> DiscountResult:
        return DiscountResult(
            coupon=None,
            discount_amount=Decimal("0.00"),
            discount_type="none",
            applied_value=Decimal("0.00"),
            final_total=context.subtotal,
            summary="No discount applied.",
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve(code: str, storefront=None) -> Coupon:
        try:
            return Coupon.objects.get(
                code=code.strip().upper(), is_active=True, storefront=storefront
            )
        except Coupon.DoesNotExist:
            raise PromotionError(f"Coupon '{code}' is invalid or inactive.")

    @staticmethod
    def _validate(coupon: Coupon, context: CartContext):
        if coupon.expires_at and coupon.expires_at < timezone.now():
            raise PromotionError("This coupon has expired.")

        if coupon.max_uses and coupon.used_count >= coupon.max_uses:
            raise PromotionError("This coupon has reached its usage limit.")

        if context.subtotal < coupon.min_order_value:
            raise PromotionError(
                f"A minimum order of ${coupon.min_order_value} is required for this coupon. "
                f"Your subtotal is ${context.subtotal}."
            )

    @staticmethod
    def _calculate(coupon: Coupon, context: CartContext) -> DiscountResult:
        if coupon.discount_type == Coupon.DiscountType.PERCENTAGE:
            raw_discount = (coupon.discount_value / Decimal("100")) * context.subtotal
            # Cap at subtotal so total never goes negative
            discount = min(raw_discount, context.subtotal).quantize(
                Decimal("0.01"), ROUND_HALF_UP
            )
            summary = f"{coupon.discount_value}% off → -${discount}"

        elif coupon.discount_type == Coupon.DiscountType.FIXED:
            discount = min(coupon.discount_value, context.subtotal).quantize(
                Decimal("0.01"), ROUND_HALF_UP
            )
            summary = f"${coupon.discount_value} off → -${discount}"

        else:
            discount = Decimal("0.00")
            summary = "No discount."

        return DiscountResult(
            coupon=coupon,
            discount_amount=discount,
            discount_type=coupon.discount_type,
            applied_value=coupon.discount_value,
            final_total=(context.subtotal - discount).quantize(
                Decimal("0.01"), ROUND_HALF_UP
            ),
            summary=summary,
        )
