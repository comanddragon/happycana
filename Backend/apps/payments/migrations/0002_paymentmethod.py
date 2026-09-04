from django.db import migrations, models


def seed_payment_methods(apps, schema_editor):
    PaymentMethod = apps.get_model("payments", "PaymentMethod")
    methods = [
        (1, "Direct Bank Transfer", "direct-bank", "Pay securely using the bank instructions sent after checkout.", "/payment-methods/direct-bank.svg", 1),
        (2, "PayPal", "paypal", "Pay with your PayPal account.", "/payment-methods/paypal.svg", 2),
        (3, "Venmo", "venmo", "Pay quickly with the Venmo app.", "/payment-methods/venmo.svg", 3),
    ]
    for pk, name, slug, description, logo_url, sort_order in methods:
        PaymentMethod.objects.update_or_create(
            slug=slug,
            defaults={
                "id": pk,
                "name": name,
                "description": description,
                "logo_url": logo_url,
                "is_active": True,
                "sort_order": sort_order,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("payments", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="PaymentMethod",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(max_length=50, unique=True)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("logo_url", models.CharField(max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
            ],
            options={"db_table": "payment_methods", "ordering": ["sort_order", "name"]},
        ),
        migrations.RunPython(seed_payment_methods, migrations.RunPython.noop),
    ]
