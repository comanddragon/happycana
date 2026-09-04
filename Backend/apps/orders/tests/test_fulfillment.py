from decimal import Decimal

import pytest
from model_bakery import baker

from apps.orders.models import Order
from services.order_fulfillment import FulfillmentService


@pytest.mark.django_db
def test_cancel_order_releases_reserved_stock():
    order = baker.make("orders.Order", status=Order.Status.PENDING)
    variant = baker.make("catalog.ProductVariant", price=Decimal("10.00"))
    baker.make("orders.OrderItem", order=order, variant=variant, quantity=2)
    stock = baker.make("inventory.Stock", variant=variant, quantity=5, reserved=2)

    FulfillmentService.cancel_order(order)

    order.refresh_from_db()
    stock.refresh_from_db()
    assert order.status == Order.Status.CANCELLED
    assert stock.reserved == 0
