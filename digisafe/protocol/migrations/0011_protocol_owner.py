# Generated by Django 4.0 on 2021-12-20 11:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0033_profile_administrator'),
        ('protocol', '0010_alter_protocol_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='protocol',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.user'),
            preserve_default=False,
        ),
    ]