# Generated by Django 4.0.4 on 2022-05-23 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pricelist', '0011_sessionprice_price_metadata_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionprice',
            name='price_metadata',
            field=models.JSONField(default=dict),
        ),
    ]
