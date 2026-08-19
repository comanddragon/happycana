
# =============================================================================
# apps/payments/managers.py
# =============================================================================
from django.db import models as db_models


class PaymentQuerySet(db_models.QuerySet):

    def for_order(self, order_id):
        return self.filter(order_id=order_id)

    def successful(self):
        return self.filter(status="success")

    def failed(self):
        return self.filter(status="failed")

    def pending(self):
        return self.filter(status="pending")

    def refunded(self):
        return self.filter(status="refunded")

    def by_gateway(self, gateway):
        return self.filter(gateway=gateway)

    def with_order(self):
        return self.select_related("order__user")

    def with_refunds(self):
        return self.prefetch_related("refunds")


class PaymentManager(db_models.Manager):
    def get_queryset(self):
        return PaymentQuerySet(self.model, using=self._db)

    def successful(self):
        return self.get_queryset().successful()

    def for_order(self, order_id):
        return self.get_queryset().for_order(order_id).with_refunds()


class RefundQuerySet(db_models.QuerySet):

    def pending(self):      return self.filter(status="pending")
    def approved(self):     return self.filter(status="approved")
    def rejected(self):     return self.filter(status="rejected")

    def for_payment(self, payment_id):
        return self.filter(payment_id=payment_id)

    def with_payment(self):
        return self.select_related("payment__order__user")


class RefundManager(db_models.Manager):
    def get_queryset(self):
        return RefundQuerySet(self.model, using=self._db)

    def pending(self):
        return self.get_queryset().pending().with_payment()


# Integrate into apps/payments/models.py:
#   Payment.objects = PaymentManager()
#   Refund.objects  = RefundManager()

