# Generated by Django 4.0 on 2021-12-13 09:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_privilegi'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='anagrafica',
            name='provincia_nascita',
        ),
        migrations.RemoveField(
            model_name='anagrafica',
            name='regione_nascita',
        ),
    ]