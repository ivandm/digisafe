# Generated by Django 4.0.4 on 2022-05-17 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pricelist', '0007_rename_extralist_extrapricelist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extrapricelist',
            name='qta',
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
    ]
