# Generated by Django 4.0.1 on 2022-04-16 07:13

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0018_diario'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Agenda',
            new_name='Agenda2',
        ),
    ]