# Generated by Django 4.0 on 2021-12-16 10:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_user_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='active',
        ),
    ]