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
    from apps.analytics.models import DailySalesSnapshot
    from apps.storefronts.models import Storefront

    target_date = (
        date.fromisoformat(date_str)
        if date_str
        else (timezone.now().date() - timedelta(days=1))
    )

    storefronts = [None, *Storefront.objects.filter(is_active=True)]
    for storefront in storefronts:
        orders = Order.objects.filter(
            storefront=storefront,
            created_at__date=target_date,
            status__in=[
                Order.Status.CONFIRMED,
                Order.Status.SHIPPED,
                Order.Status.DELIVERED,
            ],
        )
        agg = orders.aggregate(
            total_orders=Count("id"),
            total_revenue=Sum("total"),
            items_sold=Sum("items__quantity"),
        )
        total_refunds = (
            Refund.objects.filter(
                payment__order__storefront=storefront,
                created_at__date=target_date,
                status="approved",
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        total_revenue = agg["total_revenue"] or 0
        DailySalesSnapshot.objects.update_or_create(
            storefront=storefront,
            date=target_date,
            defaults={
                "total_orders": agg["total_orders"] or 0,
                "total_revenue": total_revenue,
                "total_refunds": total_refunds,
                "net_revenue": total_revenue - total_refunds,
                "new_customers": orders.values("user_id").distinct().count(),
                "items_sold": agg["items_sold"] or 0,
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
    from apps.storefronts.models import Storefront

    target_date = (
        date.fromisoformat(date_str)
        if date_str
        else (timezone.now().date() - timedelta(days=1))
    )

    storefronts = [None, *Storefront.objects.filter(is_active=True)]
    for storefront in storefronts:
        products = Product.objects.filter(is_active=True)
        if storefront is not None:
            products = products.filter(
                listings__storefront=storefront, listings__is_active=True
            ).distinct()
        for product in products:
            views = Event.objects.filter(
                storefront=storefront,
                event_type=Event.EventType.PRODUCT_VIEW,
                occurred_at__date=target_date,
                payload__product_id=str(product.id),
            ).count()

            add_to_carts = Event.objects.filter(
                storefront=storefront,
                event_type=Event.EventType.ADD_TO_CART,
                occurred_at__date=target_date,
                payload__product_id=str(product.id),
            ).count()

            purchases_agg = OrderItem.objects.filter(
                order__storefront=storefront,
                order__created_at__date=target_date,
                variant__product=product,
            ).aggregate(qty=Sum("quantity"), rev=Sum("total_price"))

            ProductPerformance.objects.update_or_create(
                storefront=storefront,
                product=product,
                date=target_date,
                defaults={
                    "views": views,
                    "add_to_carts": add_to_carts,
                    "purchases": purchases_agg["qty"] or 0,
                    "revenue": purchases_agg["rev"] or 0,
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
    from apps.storefronts.models import Storefront

    target_date = (
        date.fromisoformat(date_str)
        if date_str
        else (timezone.now().date() - timedelta(days=1))
    )

    def count_event(event_type, storefront):
        return (
            Event.objects.filter(
                storefront=storefront,
                event_type=event_type,
                occurred_at__date=target_date,
            )
            .values("session_key")
            .distinct()
            .count()
        )

    storefronts = [None, *Storefront.objects.filter(is_active=True)]
    for storefront in storefronts:
        sessions = (
            Event.objects.filter(storefront=storefront, occurred_at__date=target_date)
            .values("session_key")
            .distinct()
            .count()
        )
        purchases = Order.objects.filter(
            storefront=storefront,
            created_at__date=target_date,
            status__in=[
                Order.Status.CONFIRMED,
                Order.Status.SHIPPED,
                Order.Status.DELIVERED,
            ],
        ).count()
        ConversionFunnel.objects.update_or_create(
            storefront=storefront,
            date=target_date,
            defaults={
                "sessions": sessions,
                "product_views": count_event(Event.EventType.PRODUCT_VIEW, storefront),
                "cart_adds": count_event(Event.EventType.ADD_TO_CART, storefront),
                "checkout_starts": count_event(
                    Event.EventType.CHECKOUT_START, storefront
                ),
                "purchases": purchases,
            },
        )
