# Generated by Django 4.0 on 2021-12-28 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_new_max_learners_practice_new_max_learners_theory_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='new',
            name='theory',
            field=models.DurationField(default=0),
        ),
    ]