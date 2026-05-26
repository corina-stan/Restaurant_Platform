# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0006_remove_stockreceipt_unit_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='alert_threshold_percentage',
            field=models.PositiveIntegerField(
                default=25,
                help_text="Prag notificare stoc (%) - default 25% (un sfert)"
            ),
        ),
    ]
