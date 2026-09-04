from decimal import Decimal

from django.db import migrations


def seed_default_shipping_method(apps, schema_editor):
    ShippingMethod = apps.get_model("shipping", "ShippingMethod")
    ShippingMethod.objects.update_or_create(
        name="DHL",
        defaults={
            "carrier": "DHL",
            "price": Decimal("35.00"),
            "estimated_days_min": 1,
            "estimated_days_max": 3,
            "is_active": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [("shipping", "0002_shippingmethod_shipment_shipping_method")]

    operations = [
        migrations.RunPython(seed_default_shipping_method, migrations.RunPython.noop),
    ]
