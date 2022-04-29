# Generated by Django 4.0.1 on 2022-04-29 07:51

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0019_sessionbook_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datebook',
            name='users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]