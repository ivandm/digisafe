# Generated by Django 4.0 on 2021-12-27 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_alter_anagrafica_fiscal_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='institution',
            field=models.BooleanField(default=False),
        ),
    ]