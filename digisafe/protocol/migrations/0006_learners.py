# Generated by Django 4.0 on 2021-12-16 17:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0031_rename_direttore_profile_director_and_more'),
        ('protocol', '0005_session_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Learners',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.user')),
            ],
        ),
    ]
