from decimal import Decimal

import pytest
from model_bakery import baker

from apps.catalog.api.filters import ProductFilter
from apps.catalog.api.serializers import ProductListSerializer, ProductSerializer
from apps.catalog_cannabis.models import CannabisProfile
from core.cache import get_category_tree_cache_key, get_product_cache_key


@pytest.mark.django_db
def test_cannabis_profile_keeps_legacy_product_response_fields():
    product = baker.make("catalog.Product", kind="cannabis", base_price=Decimal("20.00"))
    effect = baker.make("catalog.Effect", name="Relaxed", slug="relaxed")
    profile = CannabisProfile.objects.create(
        product=product,
        compliance_category="flower",
        cannabis_type="indica",
        sub_type="indoor",
    )
    profile.effect_tags.add(effect)

    list_payload = ProductListSerializer(product).data
    detail_payload = ProductSerializer(product).data

    for payload in (list_payload, detail_payload):
        assert payload["compliance_category"] == "flower"
        assert payload["cannabis_type"] == "indica"
        assert payload["sub_type"] == "indoor"
        assert payload["effects"] == [{"id": str(effect.id), "name": "Relaxed", "slug": "relaxed"}]


@pytest.mark.django_db
def test_cannabis_filters_use_the_profile():
    matching = baker.make("catalog.Product", kind="cannabis")
    other = baker.make("catalog.Product", kind="cannabis")
    CannabisProfile.objects.create(product=matching, cannabis_type="sativa")
    CannabisProfile.objects.create(product=other, cannabis_type="indica")

    filtered = ProductFilter(
        data={"cannabis_type": "sativa"}, queryset=type(matching).objects.all()
    ).qs

    assert list(filtered) == [matching]


def test_cache_keys_are_namespaced_by_storefront():
    assert get_product_cache_key("product-1", "peptides") != get_product_cache_key(
        "product-1", "footwear"
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("kind", "model", "field", "value"),
    [
        ("peptide", "catalog_peptides.PeptideProfile", "purity_percent", Decimal("99.500")),
        ("footwear", "catalog_footwear.FootwearProfile", "style_code", "AJ1-RED"),
    ],
)
def test_vertical_profiles_are_exposed_by_the_shared_product_api(kind, model, field, value):
    product = baker.make("catalog.Product", kind=kind)
    baker.make(model, product=product, **{field: value})

    payload = ProductListSerializer(product).data

    assert payload["vertical_profile"]["kind"] == kind
    expected = str(value) if isinstance(value, Decimal) else value
    assert payload["vertical_profile"]["data"][field] == expected
    assert get_category_tree_cache_key("/api/catalog/categories/", "peptides") != (
        get_category_tree_cache_key("/api/catalog/categories/", "footwear")
    )
