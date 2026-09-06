from decimal import Decimal
from unittest.mock import patch

import pytest
from model_bakery import baker

from services.email import EmailService


@pytest.mark.django_db
def test_order_email_uses_storefront_sender_brand_currency_and_url():
    storefront = baker.make(
        "storefronts.Storefront",
        name="Peptide Supply",
        currency="EUR",
        frontend_url="https://peptides.example",
        from_email="orders@peptides.example",
        support_email="help@peptides.example",
    )
    user = baker.make("users.User", email="buyer@example.com")
    order = baker.make(
        "orders.Order",
        user=user,
        storefront=storefront,
        subtotal=Decimal("12.00"),
        total=Decimal("12.00"),
    )

    with patch("services.email.resend.Emails.send", return_value={"id": "email-1"}) as send:
        EmailService.send_order_placed(order)

    payload = send.call_args.args[0]
    assert payload["from"] == "orders@peptides.example"
    assert "Peptide Supply" in payload["html"]
    assert "EUR 12.00" in payload["html"]
    assert f"https://peptides.example/account/orders/{order.id}" in payload["html"]
    assert payload["to"] == ["buyer@example.com"]
