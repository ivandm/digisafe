# Generated by Django 4.0 on 2022-01-27 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0024_alter_contentcourse_course'),
        ('users', '0041_alter_profile_sign'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjects',
            name='subjects',
            field=models.ManyToManyField(blank=True, help_text='Permitted courses', to='courses.Courses'),
        ),
    ]
