from decimal import Decimal
from unittest.mock import patch

import pytest
from model_bakery import baker

from apps.orders.models import Order
from apps.payments.models import Payment, Refund
from services.payment_services import PaymentService


@pytest.mark.django_db
@patch("services.email.EmailService.send_refund_processed")
@patch("apps.payments.gateways.stripe.StripeGateway")
def test_full_refund_updates_payment_and_order(mock_gateway_class, mock_email):
    order = baker.make("orders.Order", status=Order.Status.SHIPPED)
    payment = baker.make(
        "payments.Payment",
        order=order,
        amount=Decimal("25.00"),
        status=Payment.Status.SUCCESS,
    )
    refund = baker.make(
        "payments.Refund",
        payment=payment,
        amount=Decimal("25.00"),
        status=Refund.Status.PENDING,
    )

    PaymentService.process_refund(refund)

    refund.refresh_from_db()
    payment.refresh_from_db()
    order.refresh_from_db()
    assert refund.status == Refund.Status.APPROVED
    assert payment.status == Payment.Status.REFUNDED
    assert order.status == Order.Status.REFUNDED
    mock_gateway_class.return_value.refund.assert_called_once()
    mock_email.assert_called_once_with(refund)
