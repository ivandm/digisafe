# Generated by Django 4.0 on 2021-12-20 08:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0011_courses_active'),
        ('protocol', '0009_alter_learners_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protocol',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.courses'),
        ),
    ]