from decimal import Decimal

from django.db import migrations


def seed_fedex_shipping_method(apps, schema_editor):
    ShippingMethod = apps.get_model("shipping", "ShippingMethod")
    ShippingMethod.objects.update_or_create(
        name="FedEx",
        defaults={
            "carrier": "FedEx",
            "price": Decimal("35.00"),
            "estimated_days_min": 1,
            "estimated_days_max": 3,
            "is_active": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [("shipping", "0003_seed_default_shipping_method")]

    operations = [
        migrations.RunPython(seed_fedex_shipping_method, migrations.RunPython.noop),
    ]
