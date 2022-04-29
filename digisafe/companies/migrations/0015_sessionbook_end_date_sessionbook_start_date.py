# Generated by Django 4.0.1 on 2022-04-26 06:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0014_datebook_users_delete_userbook'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionbook',
            name='end_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sessionbook',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
