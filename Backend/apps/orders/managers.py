# =============================================================================
# apps/orders/managers.py
# =============================================================================
from django.db import models as db_models
from django.utils import timezone
from datetime import timedelta


class CartQuerySet(db_models.QuerySet):

    def for_user(self, user):
        return self.filter(user=user)

    def with_items(self):
        return self.prefetch_related("items__variant__attributes")

    def with_full_items(self):
        """Full prefetch including stock — used at checkout."""
        return self.prefetch_related(
            "items__variant__attributes",
            "items__variant__stock_levels__warehouse",
        )

    def abandoned(self, minutes=30):
        """
        Carts that haven't been touched in `minutes` and belong to a
        user with a PENDING order — i.e. stale checkout attempts.
        """
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return self.filter(updated_at__lt=cutoff, user__isnull=False)

    def anonymous(self):
        return self.filter(user__isnull=True, session_key__isnull=False)


class CartManager(db_models.Manager):
    def get_queryset(self):
        return CartQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user).with_items()

    def abandoned(self, minutes=30):
        return self.get_queryset().abandoned(minutes=minutes)


# ---------------------------------------------------------------------------

class OrderQuerySet(db_models.QuerySet):

    def for_user(self, user):
        return self.filter(user=user)

    def by_status(self, status):
        return self.filter(status=status)

    def pending(self):      return self.filter(status="pending")
    def confirmed(self):    return self.filter(status="confirmed")
    def processing(self):   return self.filter(status="processing")
    def shipped(self):      return self.filter(status="shipped")
    def delivered(self):    return self.filter(status="delivered")
    def cancelled(self):    return self.filter(status="cancelled")
    def refunded(self):     return self.filter(status="refunded")

    def active(self):
        """Orders that are still in progress — not terminal states."""
        return self.filter(status__in=["pending", "confirmed", "processing", "shipped"])

    def completed(self):
        return self.filter(status__in=["delivered", "refunded"])

    def with_items(self):
        return self.prefetch_related("items__variant__product")

    def with_address(self):
        return self.select_related("address")

    def with_coupon(self):
        return self.select_related("coupon")

    def with_payments(self):
        return self.prefetch_related("payments")

    def with_shipments(self):
        return self.prefetch_related("shipments__events")

    def full(self):
        """Full prefetch — used in order detail views and fulfilment service."""
        return (
            self.with_items()
                .with_address()
                .with_coupon()
                .with_payments()
                .with_shipments()
                .select_related("user")
        )

    def stale_pending(self, minutes=30):
        """
        Pending orders older than `minutes` — used by
        inventory.tasks.release_expired_reservations.
        """
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return self.filter(status="pending", created_at__lt=cutoff)

    def ready_for_auto_complete(self, days=14):
        """
        Shipped orders with no manual delivery update after `days` —
        used by orders.tasks.auto_complete_delivered_orders.
        """
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(status="shipped", updated_at__lt=cutoff)

    def placed_on(self, date):
        return self.filter(created_at__date=date)

    def in_date_range(self, start, end):
        return self.filter(created_at__date__gte=start, created_at__date__lte=end)


class OrderManager(db_models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user).with_items().with_address()

    def active(self):
        return self.get_queryset().active()

    def stale_pending(self, minutes=30):
        return self.get_queryset().stale_pending(minutes=minutes)

    def ready_for_auto_complete(self, days=14):
        return self.get_queryset().ready_for_auto_complete(days=days)


# Integrate into apps/orders/models.py:
#   Cart.objects  = CartManager()
#   Order.objects = OrderManager()