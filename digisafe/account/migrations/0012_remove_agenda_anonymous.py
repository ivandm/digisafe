# Generated by Django 4.0.1 on 2022-04-13 10:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_agenda_delete_usersposition'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agenda',
            name='anonymous',
        ),
    ]
