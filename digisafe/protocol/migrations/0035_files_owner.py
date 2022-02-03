# Generated by Django 4.0 on 2022-01-07 08:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0039_institutions'),
        ('protocol', '0034_alter_files_options_alter_files_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='files',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.user'),
            preserve_default=False,
        ),
    ]
