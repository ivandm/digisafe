# Generated by Django 4.0 on 2022-01-06 10:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('protocol', '0031_remove_files_type_files_doc_type_alter_files_file'),
    ]

    operations = [
        migrations.RenameField(
            model_name='session',
            old_name='type',
            new_name='subject_type',
        ),
    ]