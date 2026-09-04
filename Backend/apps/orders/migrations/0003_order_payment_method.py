import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0002_order_shipping_method"),
        ("payments", "0002_paymentmethod"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="payment_method",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="orders",
                to="payments.paymentmethod",
            ),
            preserve_default=False,
        ),
    ]
