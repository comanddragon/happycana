
# =============================================================================
# apps/analytics/tasks.py
# =============================================================================
from django.tasks import task


@task()
def aggregate_daily_sales(date_str: str = None):
    """
    Computes and stores a DailySalesSnapshot for a given date.
    Defaults to yesterday. Run nightly at midnight via cron.
    """
    from django.utils import timezone
    from datetime import timedelta, date
    from django.db.models import Sum, Count
    from apps.orders.models import Order
    from apps.payments.models import Refund
    from apps.users.models import User
    from apps.analytics.models import DailySalesSnapshot

    target_date = date.fromisoformat(date_str) if date_str else (timezone.now().date() - timedelta(days=1))

    orders = Order.objects.filter(
        created_at__date = target_date,
        status__in       = [Order.Status.CONFIRMED, Order.Status.SHIPPED, Order.Status.DELIVERED],
    )

    agg = orders.aggregate(
        total_orders  = Count("id"),
        total_revenue = Sum("total"),
        items_sold    = Sum("items__quantity"),
    )

    total_refunds = Refund.objects.filter(
        created_at__date = target_date,
        status           = "approved",
    ).aggregate(total=Sum("amount"))["total"] or 0

    total_revenue = agg["total_revenue"] or 0
    net_revenue   = total_revenue - total_refunds

    new_customers = User.objects.filter(created_at__date=target_date).count()

    DailySalesSnapshot.objects.update_or_create(
        date     = target_date,
        defaults = {
            "total_orders":  agg["total_orders"] or 0,
            "total_revenue": total_revenue,
            "total_refunds": total_refunds,
            "net_revenue":   net_revenue,
            "new_customers": new_customers,
            "items_sold":    agg["items_sold"] or 0,
        },
    )


@task()
def aggregate_product_performance(date_str: str = None):
    """
    Computes per-product stats for a given date from the Event table.
    Run nightly after aggregate_daily_sales.
    """
    from django.utils import timezone
    from datetime import timedelta, date
    from django.db.models import Sum
    from apps.analytics.models import Event, ProductPerformance
    from apps.orders.models import OrderItem
    from apps.catalog.models import Product

    target_date = date.fromisoformat(date_str) if date_str else (timezone.now().date() - timedelta(days=1))

    for product in Product.objects.filter(is_active=True):
        views = Event.objects.filter(
            event_type  = Event.EventType.PRODUCT_VIEW,
            occurred_at__date = target_date,
            payload__product_id = str(product.id),
        ).count()

        add_to_carts = Event.objects.filter(
            event_type  = Event.EventType.ADD_TO_CART,
            occurred_at__date = target_date,
            payload__product_id = str(product.id),
        ).count()

        purchases_agg = OrderItem.objects.filter(
            order__created_at__date = target_date,
            variant__product        = product,
        ).aggregate(qty=Sum("quantity"), rev=Sum("total_price"))

        ProductPerformance.objects.update_or_create(
            product = product,
            date    = target_date,
            defaults = {
                "views":        views,
                "add_to_carts": add_to_carts,
                "purchases":    purchases_agg["qty"] or 0,
                "revenue":      purchases_agg["rev"] or 0,
            },
        )


@task()
def aggregate_conversion_funnel(date_str: str = None):
    """
    Computes daily conversion funnel metrics from the Event table.
    Run nightly after aggregate_product_performance.
    """
    from django.utils import timezone
    from datetime import timedelta, date
    from apps.analytics.models import Event, ConversionFunnel
    from apps.orders.models import Order

    target_date = date.fromisoformat(date_str) if date_str else (timezone.now().date() - timedelta(days=1))

    def count_event(event_type):
        return Event.objects.filter(
            event_type=event_type,
            occurred_at__date=target_date,
        ).values("session_key").distinct().count()

    sessions        = Event.objects.filter(occurred_at__date=target_date).values("session_key").distinct().count()
    product_views   = count_event(Event.EventType.PRODUCT_VIEW)
    cart_adds       = count_event(Event.EventType.ADD_TO_CART)
    checkout_starts = count_event(Event.EventType.CHECKOUT_START)
    purchases       = Order.objects.filter(
        created_at__date = target_date,
        status__in       = [Order.Status.CONFIRMED, Order.Status.SHIPPED, Order.Status.DELIVERED],
    ).count()

    ConversionFunnel.objects.update_or_create(
        date     = target_date,
        defaults = {
            "sessions":        sessions,
            "product_views":   product_views,
            "cart_adds":       cart_adds,
            "checkout_starts": checkout_starts,
            "purchases":       purchases,
        },
    )