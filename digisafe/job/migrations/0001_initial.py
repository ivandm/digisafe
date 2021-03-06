# Generated by Django 4.0.4 on 2022-06-04 16:08

from django.db import migrations, models
import job.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', job.models.UpperCaseCharField(default='', max_length=50, unique=True)),
                ('title', models.CharField(default='', max_length=255, unique=True)),
                ('description', models.TextField(blank=True, default='', max_length=1000)),
            ],
        ),
    ]
