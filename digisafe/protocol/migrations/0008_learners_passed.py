# Generated by Django 4.0 on 2021-12-16 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('protocol', '0007_learners_protocol'),
    ]

    operations = [
        migrations.AddField(
            model_name='learners',
            name='passed',
            field=models.BooleanField(default=False),
        ),
    ]
