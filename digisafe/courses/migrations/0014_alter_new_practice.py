# Generated by Django 4.0 on 2021-12-28 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0013_alter_new_theory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='new',
            name='practice',
            field=models.DurationField(default=0),
        ),
    ]
