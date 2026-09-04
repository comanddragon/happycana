from rest_framework import serializers

from .models import Storefront


class StorefrontSerializer(serializers.ModelSerializer):
    domains = serializers.SlugRelatedField(many=True, read_only=True, slug_field="domain")
    origins = serializers.SlugRelatedField(many=True, read_only=True, slug_field="origin")

    class Meta:
        model = Storefront
        fields = [
            "id", "slug", "name", "kind", "currency", "frontend_url",
            "support_email", "branding", "settings", "domains", "origins",
        ]
        read_only_fields = fields
