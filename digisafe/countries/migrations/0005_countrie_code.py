# Generated by Django 4.0 on 2021-12-08 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('countries', '0004_remove_city_state_province_city_province'),
    ]

    operations = [
        migrations.AddField(
            model_name='countrie',
            name='code',
            field=models.CharField(default='', max_length=2),
        ),
    ]