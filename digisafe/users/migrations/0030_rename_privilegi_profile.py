# Generated by Django 4.0 on 2021-12-16 10:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_remove_user_active'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Privilegi',
            new_name='Profile',
        ),
    ]