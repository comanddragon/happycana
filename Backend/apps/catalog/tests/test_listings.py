from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from model_bakery import baker

from apps.catalog.models import Listing


@pytest.mark.django_db
def test_listing_can_override_price_without_changing_product():
    store = baker.make("storefronts.Storefront")
    product = baker.make("catalog.Product", base_price=Decimal("100.00"))
    listing = Listing.objects.create(
        storefront=store,
        product=product,
        slug="store-product",
        price_override=Decimal("85.00"),
    )

    assert listing.effective_price == Decimal("85.00")
    assert product.base_price == Decimal("100.00")


@pytest.mark.django_db
def test_listing_slug_is_unique_within_a_storefront_but_reusable_across_stores():
    first_store = baker.make("storefronts.Storefront")
    second_store = baker.make("storefronts.Storefront")
    Listing.objects.create(
        storefront=first_store,
        product=baker.make("catalog.Product"),
        slug="shared-slug",
    )
    Listing.objects.create(
        storefront=second_store,
        product=baker.make("catalog.Product"),
        slug="shared-slug",
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        Listing.objects.create(
            storefront=first_store,
            product=baker.make("catalog.Product"),
            slug="shared-slug",
        )
