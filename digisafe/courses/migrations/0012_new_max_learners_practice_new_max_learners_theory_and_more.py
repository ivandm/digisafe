# Generated by Django 4.0 on 2021-12-27 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0011_courses_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='new',
            name='max_learners_practice',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='new',
            name='max_learners_theory',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='update',
            name='max_learners_practice',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='update',
            name='max_learners_theory',
            field=models.IntegerField(default=0),
        ),
    ]
