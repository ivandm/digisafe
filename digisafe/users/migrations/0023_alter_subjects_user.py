# Generated by Django 4.0 on 2021-12-16 09:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_remove_subjects_course_subjects_courses'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjects',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='materie', to='users.user'),
        ),
    ]
