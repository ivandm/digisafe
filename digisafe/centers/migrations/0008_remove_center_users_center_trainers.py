# Generated by Django 4.0.1 on 2022-02-20 10:47

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('centers', '0007_center_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='center',
            name='users',
        ),
        migrations.AddField(
            model_name='center',
            name='trainers',
            field=models.ManyToManyField(blank=True, related_name='associate_trainers', to=settings.AUTH_USER_MODEL),
        ),
    ]