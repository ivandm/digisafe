# Generated by Django 4.0 on 2022-01-06 20:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('protocol', '0033_alter_files_file'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='files',
            options={'ordering': ['id']},
        ),
        migrations.AlterUniqueTogether(
            name='files',
            unique_together={('protocol', 'doc_type')},
        ),
    ]