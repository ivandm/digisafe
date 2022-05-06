# Generated by Django 4.0.4 on 2022-05-06 09:45

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0026_sessionbook_user_decline_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionbook',
            name='user_decline_list',
            field=models.ManyToManyField(blank=True, related_name='sessionbook_user_decline', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='sessionbook',
            name='user_option_list',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
