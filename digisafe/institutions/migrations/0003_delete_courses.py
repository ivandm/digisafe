# Generated by Django 4.0 on 2022-01-04 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0002_courses'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Courses',
        ),
    ]
