from decimal import Decimal

import pytest
from model_bakery import baker
from rest_framework.test import APIClient

from apps.notifications.models import Notification
from apps.orders.models import Cart
from services.checkout import CheckoutService


@pytest.mark.django_db
def test_user_has_an_independent_cart_per_storefront():
    user = baker.make("users.User")
    peptides = baker.make("storefronts.Storefront", slug="peptides")
    footwear = baker.make("storefronts.Storefront", slug="footwear")
    client = APIClient()
    client.force_authenticate(user)

    peptide_response = client.get("/api/orders/cart/", HTTP_X_STOREFRONT=peptides.slug)
    footwear_response = client.get("/api/orders/cart/", HTTP_X_STOREFRONT=footwear.slug)

    assert peptide_response.status_code == 200
    assert footwear_response.status_code == 200
    assert peptide_response.data["id"] != footwear_response.data["id"]
    assert Cart.objects.filter(user=user).count() == 2


@pytest.mark.django_db
def test_order_list_does_not_cross_storefront_boundary():
    user = baker.make("users.User")
    peptides = baker.make("storefronts.Storefront", slug="peptides")
    footwear = baker.make("storefronts.Storefront", slug="footwear")
    peptide_order = baker.make(
        "orders.Order", user=user, storefront=peptides, total=Decimal("10.00")
    )
    baker.make("orders.Order", user=user, storefront=footwear, total=Decimal("20.00"))
    client = APIClient()
    client.force_authenticate(user)

    response = client.get("/api/orders/", HTTP_X_STOREFRONT=peptides.slug)

    assert response.status_code == 200
    assert [item["id"] for item in response.data["results"]] == [str(peptide_order.id)]


@pytest.mark.django_db
def test_checkout_configuration_is_scoped_to_storefront():
    peptides = baker.make("storefronts.Storefront", slug="peptides")
    hash_store = baker.make("storefronts.Storefront", slug="hash")
    footwear = baker.make("storefronts.Storefront", slug="footwear")
    peptide_payment = baker.make(
        "payments.PaymentMethod", is_global=False, slug="card", is_active=True
    )
    peptide_payment.storefronts.add(peptides, hash_store)
    global_payment = baker.make(
        "payments.PaymentMethod", is_global=True, slug="bank", is_active=True
    )
    footwear_payment = baker.make(
        "payments.PaymentMethod", is_global=False, slug="card", is_active=True
    )
    footwear_payment.storefronts.add(footwear)
    peptide_shipping = baker.make(
        "shipping.ShippingMethod", is_global=False, is_active=True
    )
    peptide_shipping.storefronts.add(peptides, hash_store)
    global_shipping = baker.make(
        "shipping.ShippingMethod", is_global=True, is_active=True
    )
    footwear_shipping = baker.make("shipping.ShippingMethod", is_global=False, is_active=True)
    footwear_shipping.storefronts.add(footwear)
    client = APIClient()

    payments = client.get("/api/payments/methods/", HTTP_X_STOREFRONT=peptides.slug)
    shipping = client.get("/api/shipping/methods/", HTTP_X_STOREFRONT=peptides.slug)
    hash_payments = client.get("/api/payments/methods/", HTTP_X_STOREFRONT=hash_store.slug)
    hash_shipping = client.get("/api/shipping/methods/", HTTP_X_STOREFRONT=hash_store.slug)

    assert payments.status_code == 200
    payment_ids = {item["id"] for item in payments.data}
    assert {peptide_payment.id, global_payment.id} <= payment_ids
    assert footwear_payment.id not in payment_ids
    assert peptide_payment.id in {item["id"] for item in hash_payments.data}
    assert shipping.status_code == 200
    shipping_ids = {item["id"] for item in shipping.data["results"]}
    assert {str(peptide_shipping.id), str(global_shipping.id)} <= shipping_ids
    assert str(footwear_shipping.id) not in shipping_ids
    assert str(peptide_shipping.id) in {
        item["id"] for item in hash_shipping.data["results"]
    }


@pytest.mark.django_db
def test_unknown_explicit_storefront_is_rejected():
    response = APIClient().get("/api/payments/methods/", HTTP_X_STOREFRONT="unknown")

    assert response.status_code == 404


@pytest.mark.django_db
def test_storefront_checkout_records_store_and_exact_stock_source():
    storefront = baker.make("storefronts.Storefront", slug="peptides")
    user = baker.make("users.User")
    address = baker.make("users.Address", user=user)
    product = baker.make("catalog.Product", kind="peptide")
    baker.make(
        "catalog.Listing",
        storefront=storefront,
        product=product,
        is_active=True,
        price_override=Decimal("12.00"),
    )
    variant = baker.make("catalog.ProductVariant", product=product, price=Decimal("15.00"))
    warehouse = baker.make("inventory.Warehouse", storefront=storefront)
    stock = baker.make(
        "inventory.Stock", variant=variant, warehouse=warehouse, quantity=10, reserved=0
    )
    cart = baker.make("orders.Cart", user=user, storefront=storefront)
    baker.make("orders.CartItem", cart=cart, variant=variant, quantity=2)
    shipping = baker.make(
        "shipping.ShippingMethod", is_global=True, is_active=True, price=Decimal("5.00")
    )
    payment = baker.make("payments.PaymentMethod", is_global=True, is_active=True)

    order = CheckoutService.create_order(
        user=user,
        address_id=address.id,
        shipping_method_id=shipping.id,
        payment_method_id=payment.id,
        storefront=storefront,
    )

    stock.refresh_from_db()
    item = order.items.get()
    assert order.storefront == storefront
    assert order.total == Decimal("29.00")
    assert item.unit_price == Decimal("12.00")
    assert item.fulfillment_warehouse == warehouse
    assert stock.reserved == 2
    assert not cart.items.exists()
    assert Notification.objects.filter(user=user, storefront=storefront).exists()


@pytest.mark.django_db
def test_storefront_checkout_can_reserve_global_warehouse_stock():
    storefront = baker.make("storefronts.Storefront", slug="dispensary")
    user = baker.make("users.User")
    address = baker.make("users.Address", user=user)
    product = baker.make("catalog.Product")
    baker.make("catalog.Listing", storefront=storefront, product=product, is_active=True)
    variant = baker.make("catalog.ProductVariant", product=product, price=Decimal("10.00"))
    warehouse = baker.make("inventory.Warehouse", storefront=None)
    stock = baker.make("inventory.Stock", variant=variant, warehouse=warehouse, quantity=5, reserved=0)
    cart = baker.make("orders.Cart", user=user, storefront=storefront)
    baker.make("orders.CartItem", cart=cart, variant=variant, quantity=1)
    shipping = baker.make("shipping.ShippingMethod", is_global=True, is_active=True, price=Decimal("0"))
    payment = baker.make("payments.PaymentMethod", is_global=True, is_active=True)

    order = CheckoutService.create_order(
        user=user,
        address_id=address.id,
        shipping_method_id=shipping.id,
        payment_method_id=payment.id,
        storefront=storefront,
    )

    stock.refresh_from_db()
    assert order.items.get().fulfillment_warehouse == warehouse
    assert stock.reserved == 1
