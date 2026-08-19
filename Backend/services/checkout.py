# =============================================================================
# services/checkout.py
# Orchestrates the full cart → order → stock reservation → payment flow.
# =============================================================================
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from apps.orders.models import Cart, Order, OrderItem
from apps.inventory.models import Stock
from apps.promotions.models import Coupon
from apps.payments.models import Payment
from apps.notifications.models import Notification


class CheckoutError(Exception):
    pass


class CheckoutService:

    @classmethod
    @transaction.atomic
    def create_order(cls, user, address_id, coupon_code=None):
        """
        Full checkout pipeline:
          1. Validate cart is not empty
          2. Validate & reserve stock for every item
          3. Apply coupon if provided
          4. Calculate totals
          5. Create Order + OrderItems
          6. Decrement stock reservations
          7. Clear the cart
          8. Trigger confirmation notification
        Returns the created Order instance.
        """
        cart = cls._get_cart(user)
        items = list(cart.items.select_related("variant__stock_levels").all())

        if not items:
            raise CheckoutError("Your cart is empty.")

        # 1. Validate & reserve stock
        stock_reservations = cls._reserve_stock(items)

        # 2. Resolve coupon & calculate totals via PromotionEngine
        from apps.promotions.engine import PromotionEngine, CartContext
        subtotal      = cls._calculate_subtotal(items)
        shipping_cost = cls._calculate_shipping(items)

        if coupon_code:
            ctx    = CartContext(subtotal=subtotal, item_count=len(items))
            result = PromotionEngine.apply_coupon(coupon_code, ctx)
            coupon   = result.coupon
            discount = result.discount_amount
        else:
            coupon   = None
            discount = Decimal("0.00")

        total = max(Decimal("0.00"), subtotal - discount + shipping_cost)

        # 3. Create Order
        order = Order.objects.create(
            user            = user,
            address_id      = address_id,
            coupon          = coupon,
            status          = Order.Status.PENDING,
            subtotal        = subtotal,
            discount_amount = discount,
            shipping_cost   = shipping_cost,
            total           = total,
        )

        # 4. Create OrderItems
        OrderItem.objects.bulk_create([
            OrderItem(
                order       = order,
                variant     = item.variant,
                quantity    = item.quantity,
                unit_price  = item.variant.price,
                total_price = item.variant.price * item.quantity,
            )
            for item in items
        ])

        # 5. Commit stock reservations
        cls._commit_stock_reservations(stock_reservations)

        # 6. Increment coupon usage
        if coupon:
            Coupon.objects.filter(id=coupon.id).update(used_count=coupon.used_count + 1)

        # 7. Clear cart
        cart.items.all().delete()

        # 8. Notify user
        Notification.objects.create(
            user  = user,
            type  = Notification.Type.ORDER,
            title = "Order Placed",
            body  = f"Your order #{order.id} has been placed successfully. Total: ${order.total}",
        )

        return order

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_cart(user):
        try:
            return Cart.objects.prefetch_related(
                "items__variant__stock_levels__warehouse"
            ).get(user=user)
        except Cart.DoesNotExist:
            raise CheckoutError("No active cart found.")

    @staticmethod
    def _reserve_stock(items):
        """
        Checks availability and increments the reserved counter for every
        item. Done inside the atomic transaction so concurrent checkouts
        can't oversell. Returns a list of (stock, qty) tuples to commit.
        """
        reservations = []
        for item in items:
            stock = (
                item.variant.stock_levels
                .select_for_update()          # row-level DB lock
                .filter(quantity__gt=0)
                .first()
            )
            if not stock:
                raise CheckoutError(
                    f"'{item.variant.sku}' is out of stock."
                )
            if stock.available < item.quantity:
                raise CheckoutError(
                    f"Only {stock.available} units of '{item.variant.sku}' available."
                )
            stock.reserved += item.quantity
            reservations.append((stock, item.quantity))
        return reservations

    @staticmethod
    def _commit_stock_reservations(reservations):
        for stock, _ in reservations:
            stock.save(update_fields=["reserved"])

    @staticmethod
    def _calculate_subtotal(items):
        return sum(item.variant.price * item.quantity for item in items)

    @staticmethod
    def _calculate_shipping(items):
        # Placeholder — plug in your shipping rate provider here
        # e.g. call ShippingService.calculate_rate(items, address)
        return Decimal("5.99")

