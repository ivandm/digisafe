# Generated by Django 4.0 on 2021-12-16 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_remove_courses_name'),
        ('users', '0014_alter_subjects_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='subjects',
            unique_together=set(),
        ),
    ]
