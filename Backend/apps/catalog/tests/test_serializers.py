import pytest

from apps.catalog.api.serializers import (
    ProductVariantWriteSerializer,
    ProductWriteSerializer,
)


@pytest.mark.django_db
def test_product_write_serializer_exposes_declared_relations():
    serializer = ProductWriteSerializer()

    assert "brand" in serializer.fields
    assert "effects" in serializer.fields


@pytest.mark.django_db
def test_variant_write_serializer_only_exposes_model_fields():
    serializer = ProductVariantWriteSerializer()

    assert "image" not in serializer.fields
    assert set(serializer.fields) == {"sku", "price", "is_active", "attributes"}
