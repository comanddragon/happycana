# =============================================================================
# services/payment_service.py
# Centralises payment confirmation and refund orchestration.
# =============================================================================
from django.db import transaction
from apps.payments.models import Payment, Refund
from apps.orders.state_machine import OrderStateMachine
from services.order_fulfillment import FulfillmentService
from apps.notifications.models import Notification


class PaymentService:
    @classmethod
    @transaction.atomic
    def confirm_payment(cls, order, gateway, gateway_ref, amount, currency="USD"):
        """
        Records a successful payment and triggers order confirmation.
        Called by the Stripe/PayPal webhook handler.
        """
        payment = Payment.objects.create(
            order=order,
            gateway=gateway,
            gateway_ref=gateway_ref,
            amount=amount,
            currency=currency,
            status=Payment.Status.SUCCESS,
        )
        FulfillmentService.confirm_order(order)
        return payment

    @classmethod
    @transaction.atomic
    def fail_payment(cls, order, gateway, gateway_ref, amount, currency="USD"):
        """Records a failed payment attempt."""
        return Payment.objects.create(
            order=order,
            gateway=gateway,
            gateway_ref=gateway_ref,
            amount=amount,
            currency=currency,
            status=Payment.Status.FAILED,
        )

    @classmethod
    @transaction.atomic
    def process_refund(cls, refund):
        """
        Calls the gateway to process the refund, then marks it approved/rejected.
        """
        from apps.payments.gateways.stripe import StripeGateway

        gateway = StripeGateway()
        try:
            gateway.refund(refund.payment.gateway_ref, float(refund.amount))
            refund.status = Refund.Status.APPROVED
            refund.save(update_fields=["status"])

            # Mark the original payment as refunded if fully refunded
            total_refunded = sum(
                r.amount
                for r in refund.payment.refunds.filter(status=Refund.Status.APPROVED)
            )
            if total_refunded >= refund.payment.amount:
                refund.payment.status = Payment.Status.REFUNDED
                refund.payment.save(update_fields=["status"])
                sm = OrderStateMachine(refund.payment.order)
                sm.refund()

            Notification.objects.create(
                storefront=refund.payment.order.storefront,
                user=refund.payment.order.user,
                type=Notification.Type.PAYMENT,
                title="Refund Processed",
                body=f"Your refund of ${refund.amount} has been processed.",
            )
            from services.email import EmailService

            EmailService.send_refund_processed(refund)

        except Exception:
            refund.status = Refund.Status.REJECTED
            refund.save(update_fields=["status"])
            raise
