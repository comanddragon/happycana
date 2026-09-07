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

    with (
        patch(
            "services.email.EmailService._download_logo",
            return_value=("encoded-image", "image/png"),
        ),
        patch("services.email.resend.Emails.send", return_value={"id": "email-1"}) as send,
    ):
        EmailService.send_order_placed(order)

    payload = send.call_args.args[0]
    assert payload["from"] == "orders@peptides.example"
    assert "Peptide Supply" in payload["html"]
    assert "EUR 12.00" in payload["html"]
    assert f"https://peptides.example/account/orders/{order.id}" in payload["html"]
    assert payload["to"] == ["buyer@example.com"]


@pytest.mark.django_db
def test_order_email_embeds_remote_logo_as_an_inline_attachment():
    logo_url = "https://storage.example/static/branding/store-logo.png"
    storefront = baker.make(
        "storefronts.Storefront",
        name="Example Store",
        logo_url=logo_url,
    )
    user = baker.make("users.User", email="buyer@example.com")
    order = baker.make(
        "orders.Order",
        user=user,
        storefront=storefront,
        subtotal=Decimal("12.00"),
        total=Decimal("12.00"),
    )

    with (
        patch(
            "services.email.EmailService._download_logo",
            return_value=("encoded-image", "image/png"),
        ),
        patch("services.email.resend.Emails.send", return_value={"id": "email-1"}) as send,
    ):
        EmailService.send_order_placed(order)

    payload = send.call_args.args[0]
    assert 'src="cid:store-logo"' in payload["html"]
    assert 'width="220"' in payload["html"]
    assert payload["attachments"] == [
        {
            "content": "encoded-image",
            "filename": "store-logo.png",
            "content_type": "image/png",
            "content_id": "store-logo",
        }
    ]
