# =============================================================================
# services/order_fulfillment.py
# Handles post-payment order lifecycle:
# confirming, fulfilling, and cancelling orders.
# =============================================================================
from django.db import transaction
from apps.orders.models import Order
from apps.inventory.models import Stock, StockMovement
from apps.notifications.models import Notification
from services.email import EmailService
from services.sms import SMSService


class FulfillmentService:

    @classmethod
    @transaction.atomic
    def confirm_order(cls, order):
        """
        Called after a successful payment.
        Moves order from PENDING → CONFIRMED and notifies the user.
        """
        if order.status != Order.Status.PENDING:
            raise ValueError(f"Cannot confirm an order with status '{order.status}'.")

        order.status = Order.Status.CONFIRMED
        order.save(update_fields=["status"])

        EmailService.send_order_confirmation(order)
        Notification.objects.create(
            user  = order.user,
            type  = Notification.Type.ORDER,
            title = "Order Confirmed",
            body  = f"Order #{order.id} is confirmed and being prepared.",
        )

    @classmethod
    @transaction.atomic
    def mark_shipped(cls, order, shipment):
        """
        Moves order CONFIRMED/PROCESSING → SHIPPED.
        Converts stock reservations into actual deductions.
        """
        if order.status not in (Order.Status.CONFIRMED, Order.Status.PROCESSING):
            raise ValueError(f"Cannot ship an order with status '{order.status}'.")

        order.status = Order.Status.SHIPPED
        order.save(update_fields=["status"])

        # Deduct stock and release reservation
        for item in order.items.select_related("variant").all():
            stock = (
                Stock.objects.select_for_update()
                .filter(variant=item.variant)
                .first()
            )
            if stock:
                stock.quantity -= item.quantity
                stock.reserved -= item.quantity
                stock.save(update_fields=["quantity", "reserved"])
                StockMovement.objects.create(
                    stock          = stock,
                    quantity_delta = -item.quantity,
                    reason         = StockMovement.Reason.SALE,
                )

        EmailService.send_order_shipped(order, shipment)
        SMSService.send_order_shipped(order, shipment.tracking_number)
        Notification.objects.create(
            user  = order.user,
            type  = Notification.Type.SHIPMENT,
            title = "Order Shipped",
            body  = f"Your order #{order.id} is on its way! Tracking: {shipment.tracking_number}",
        )

    @classmethod
    @transaction.atomic
    def mark_delivered(cls, order):
        if order.status != Order.Status.SHIPPED:
            raise ValueError(f"Cannot mark delivered an order with status '{order.status}'.")

        order.status = Order.Status.DELIVERED
        order.save(update_fields=["status"])

        SMSService.send_delivery_confirmation(order)
        EmailService.send_order_delivered(order)
        Notification.objects.create(
            user  = order.user,
            type  = Notification.Type.ORDER,
            title = "Order Delivered",
            body  = f"Your order #{order.id} has been delivered. Enjoy!",
        )

    @classmethod
    @transaction.atomic
    def cancel_order(cls, order):
        """
        Cancels an order and releases any stock reservations.
        Only allowed before shipment.
        """
        if order.status in (Order.Status.SHIPPED, Order.Status.DELIVERED):
            raise ValueError("Cannot cancel an order that has already shipped.")

        # Release reserved stock
        for item in order.items.select_related("variant").all():
            Stock.objects.filter(variant=item.variant).update(
                reserved=models.F("reserved") - item.quantity
            )

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])

        Notification.objects.create(
            user  = order.user,
            type  = Notification.Type.ORDER,
            title = "Order Cancelled",
            body  = f"Your order #{order.id} has been cancelled.",
        )

