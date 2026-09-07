"""Operational data for the Unfold admin landing page."""

from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, ExpressionWrapper, F, IntegerField, Sum
from django.db.models.functions import TruncDate
from django.urls import reverse
from django.utils import timezone

from apps.catalog.models import Product
from apps.inventory.models import Stock
from apps.orders.models import Order
from apps.storefronts.models import Storefront

REVENUE_STATUSES = (
    Order.Status.CONFIRMED,
    Order.Status.PROCESSING,
    Order.Status.SHIPPED,
    Order.Status.DELIVERED,
)


def _change(current: Decimal | int, previous: Decimal | int) -> dict[str, object]:
    current_value = Decimal(current or 0)
    previous_value = Decimal(previous or 0)
    if previous_value == 0:
        percentage = 100 if current_value > 0 else 0
    else:
        percentage = round(((current_value - previous_value) / previous_value) * 100, 1)
    return {
        "delta": abs(percentage),
        "direction": "up" if percentage > 0 else "down" if percentage < 0 else "flat",
    }


def _money(value: Decimal | int, currency: str = "USD") -> str:
    symbols = {"USD": "$", "GBP": "£", "EUR": "€", "NGN": "₦"}
    return f"{symbols.get(currency, f'{currency} ')}{Decimal(value or 0):,.2f}"


def dashboard_callback(request, context):
    """Add fast, aggregate commerce metrics to the admin index context."""
    today = timezone.localdate()
    current_hour = timezone.localtime().hour
    greeting = (
        "Good morning"
        if current_hour < 12
        else "Good afternoon"
        if current_hour < 18
        else "Good evening"
    )
    period_start = today - timedelta(days=29)
    previous_start = period_start - timedelta(days=30)
    previous_end = period_start - timedelta(days=1)

    revenue_orders = Order.objects.filter(status__in=REVENUE_STATUSES)
    current_orders = revenue_orders.filter(
        created_at__date__range=(period_start, today)
    )
    previous_orders = revenue_orders.filter(
        created_at__date__range=(previous_start, previous_end)
    )

    current_summary = current_orders.aggregate(
        revenue=Sum("total", default=Decimal("0")),
        orders=Count("id"),
        customers=Count("user_id", distinct=True),
    )
    previous_summary = previous_orders.aggregate(
        revenue=Sum("total", default=Decimal("0")),
        orders=Count("id"),
        customers=Count("user_id", distinct=True),
    )

    active_products = Product.objects.filter(is_active=True).count()
    available_stock = ExpressionWrapper(
        F("quantity") - F("reserved"), output_field=IntegerField()
    )
    low_stock = (
        Stock.objects.annotate(available_units=available_stock)
        .filter(available_units__lte=5, variant__is_active=True)
        .count()
    )

    daily_rows = {
        row["day"]: row
        for row in current_orders.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(revenue=Sum("total"), orders=Count("id"))
        .order_by("day")
    }
    chart_days = [today - timedelta(days=13 - offset) for offset in range(14)]
    revenue_chart = {
        "labels": [day.strftime("%b %-d") for day in chart_days],
        "datasets": [
            {
                "label": "Revenue",
                "data": [
                    float(daily_rows.get(day, {}).get("revenue") or 0)
                    for day in chart_days
                ],
                "borderColor": "#9333ea",
                "backgroundColor": "rgba(147, 51, 234, 0.12)",
                "fill": True,
                "tension": 0.35,
                "pointRadius": 2,
                "pointHoverRadius": 5,
            }
        ],
    }
    revenue_chart_options = {
        "maintainAspectRatio": False,
        "plugins": {"legend": {"display": False}},
        "scales": {
            "x": {"grid": {"display": False}},
            "y": {"beginAtZero": True, "grid": {"color": "rgba(148, 163, 184, .16)"}},
        },
    }

    status_counts = dict(
        Order.objects.filter(created_at__date__gte=period_start)
        .values_list("status")
        .annotate(total=Count("id"))
    )
    status_total = sum(status_counts.values()) or 1
    status_rows = [
        {
            "dashboard_greeting": greeting,
            "label": label,
            "count": status_counts.get(value, 0),
            "percentage": round(status_counts.get(value, 0) / status_total * 100),
            "tone": {
                Order.Status.PENDING: "amber",
                Order.Status.CANCELLED: "red",
                Order.Status.REFUNDED: "red",
                Order.Status.DELIVERED: "green",
            }.get(value, "purple"),
        }
        for value, label in Order.Status.choices
        if status_counts.get(value, 0)
    ]

    storefront_rows = []
    storefront_metrics = {
        row["storefront_id"]: row
        for row in current_orders.values("storefront_id").annotate(
            revenue=Sum("total", default=Decimal("0")),
            orders=Count("id"),
        )
    }
    max_store_revenue = max(
        (Decimal(row["revenue"] or 0) for row in storefront_metrics.values()),
        default=Decimal("0"),
    )
    for storefront in Storefront.objects.filter(is_active=True).order_by("name"):
        metrics = storefront_metrics.get(storefront.id, {})
        revenue = Decimal(metrics.get("revenue") or 0)
        storefront_rows.append(
            {
                "name": storefront.name,
                "kind": storefront.get_kind_display(),
                "orders": metrics.get("orders", 0),
                "revenue": _money(revenue, storefront.currency),
                "share": round(revenue / max_store_revenue * 100)
                if max_store_revenue
                else 0,
            }
        )

    recent_orders = []
    for order in Order.objects.select_related("user", "storefront").order_by(
        "-created_at"
    )[:7]:
        recent_orders.append(
            {
                "id": order.short_id,
                "url": reverse("admin:orders_order_change", args=[order.pk]),
                "customer": order.user.email,
                "storefront": order.storefront.name if order.storefront else "Legacy",
                "status": order.get_status_display(),
                "status_key": order.status,
                "total": _money(
                    order.total,
                    order.storefront.currency if order.storefront else "USD",
                ),
                "date": timezone.localtime(order.created_at).strftime("%b %-d, %H:%M"),
            }
        )

    context.update(
        {
            "dashboard_period": f"{period_start:%b %-d} - {today:%b %-d, %Y}",
            "dashboard_kpis": [
                {
                    "label": "Confirmed revenue",
                    "value": _money(current_summary["revenue"]),
                    "icon": "payments",
                    **_change(current_summary["revenue"], previous_summary["revenue"]),
                },
                {
                    "label": "Orders",
                    "value": f"{current_summary['orders']:,}",
                    "icon": "receipt_long",
                    **_change(current_summary["orders"], previous_summary["orders"]),
                },
                {
                    "label": "Purchasing customers",
                    "value": f"{current_summary['customers']:,}",
                    "icon": "group",
                    **_change(
                        current_summary["customers"], previous_summary["customers"]
                    ),
                },
                {
                    "label": "Active products",
                    "value": f"{active_products:,}",
                    "icon": "inventory_2",
                    "direction": "alert" if low_stock else "flat",
                    "value_note": f"{low_stock} low-stock item{'s' if low_stock != 1 else ''}",
                },
            ],
            "revenue_chart": json.dumps(revenue_chart),
            "revenue_chart_options": json.dumps(revenue_chart_options),
            "status_rows": status_rows,
            "storefront_rows": storefront_rows,
            "recent_orders": recent_orders,
            "orders_url": reverse("admin:orders_order_changelist"),
            "products_url": reverse("admin:catalog_product_changelist"),
        }
    )
    return context
