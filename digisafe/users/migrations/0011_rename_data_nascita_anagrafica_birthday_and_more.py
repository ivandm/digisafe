# Generated by Django 4.0 on 2021-12-13 17:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_remove_anagrafica_provincia_nascita_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='anagrafica',
            old_name='data_nascita',
            new_name='birthday',
        ),
        migrations.RenameField(
            model_name='anagrafica',
            old_name='citta_nascita',
            new_name='city',
        ),
        migrations.RenameField(
            model_name='anagrafica',
            old_name='stato_nascita',
            new_name='country',
        ),
    ]
