# Generated by Django 3.2.7 on 2021-12-08 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_anagrafica_data_nascita'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anagrafica',
            name='data_nascita',
            field=models.DateField(null=True),
        ),
    ]