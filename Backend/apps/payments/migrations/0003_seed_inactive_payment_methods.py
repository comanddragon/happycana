from django.db import migrations


def seed_inactive_payment_methods(apps, schema_editor):
    PaymentMethod = apps.get_model("payments", "PaymentMethod")
    # 0002 seeded explicit primary keys, so PostgreSQL's identity sequence may
    # still point at 1. Advance it before creating rows with automatic IDs.
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(
            "SELECT setval(pg_get_serial_sequence('payment_methods', 'id'), "
            "COALESCE(MAX(id), 1), true) FROM payment_methods"
        )
    methods = [
        ("Credit or Debit Card", "card", "Pay with Visa, Mastercard, American Express, or Discover.", "/payment-methods/card.svg", 10),
        ("Apple Pay", "apple-pay", "Pay securely from an Apple device.", "/payment-methods/apple-pay.svg", 11),
        ("Google Pay", "google-pay", "Pay securely with a saved Google Pay method.", "/payment-methods/google-pay.svg", 12),
        ("Cash App Pay", "cash-app-pay", "Pay using the Cash App mobile app.", "/payment-methods/cash-app-pay.svg", 13),
        ("Zelle", "zelle", "Send payment through a participating bank or credit union.", "/payment-methods/zelle.svg", 14),
    ]
    for name, slug, description, logo_url, sort_order in methods:
        PaymentMethod.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "description": description,
                "logo_url": logo_url,
                "is_active": False,
                "sort_order": sort_order,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("payments", "0002_paymentmethod")]

    operations = [
        migrations.RunPython(seed_inactive_payment_methods, migrations.RunPython.noop),
    ]
