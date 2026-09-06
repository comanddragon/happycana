import pytest
from model_bakery import baker
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_category_tree_is_scoped_to_storefront():
    peptides = baker.make("storefronts.Storefront", slug="peptides")
    dispensary = baker.make("storefronts.Storefront", slug="dispensary")
    peptide_category = baker.make("catalog.Category", slug="research-peptides", parent=None)
    cannabis_category = baker.make("catalog.Category", slug="flower", parent=None)
    peptide_product = baker.make("catalog.Product", kind="peptide")
    cannabis_product = baker.make("catalog.Product", kind="cannabis")
    peptide_listing = baker.make("catalog.Listing", storefront=peptides, product=peptide_product)
    cannabis_listing = baker.make("catalog.Listing", storefront=dispensary, product=cannabis_product)
    peptide_listing.categories.add(peptide_category)
    cannabis_listing.categories.add(cannabis_category)

    response = APIClient().get("/api/catalog/categories/", HTTP_X_STOREFRONT="peptides")

    assert response.status_code == 200
    results = response.data["results"] if isinstance(response.data, dict) else response.data
    assert [item["slug"] for item in results] == ["research-peptides"]


@pytest.mark.django_db
def test_brands_and_effects_are_scoped_to_storefront():
    peptides = baker.make("storefronts.Storefront", slug="peptides")
    dispensary = baker.make("storefronts.Storefront", slug="dispensary")
    cannabis_brand = baker.make("catalog.Brand", slug="cannabis-brand")
    cannabis_product = baker.make("catalog.Product", kind="cannabis", brand=cannabis_brand)
    baker.make("catalog.Listing", storefront=dispensary, product=cannabis_product)
    profile = baker.make("catalog_cannabis.CannabisProfile", product=cannabis_product)
    effect = baker.make("catalog.Effect", slug="relaxed")
    profile.effect_tags.add(effect)
    peptide_product = baker.make("catalog.Product", kind="peptide")
    baker.make("catalog.Listing", storefront=peptides, product=peptide_product)

    client = APIClient()
    brands = client.get("/api/catalog/brands/", HTTP_X_STOREFRONT="peptides")
    effects = client.get("/api/catalog/effects/", HTTP_X_STOREFRONT="peptides")

    brand_results = brands.data["results"] if isinstance(brands.data, dict) else brands.data
    effect_results = effects.data["results"] if isinstance(effects.data, dict) else effects.data
    assert brand_results == []
    assert effect_results == []
