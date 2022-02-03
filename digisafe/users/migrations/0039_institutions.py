# Generated by Django 4.0 on 2022-01-04 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0001_initial'),
        ('users', '0038_auto_20220101_1835'),
    ]

    operations = [
        migrations.CreateModel(
            name='Institutions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField(blank=True, default='')),
                ('institutions', models.ManyToManyField(blank=True, help_text='Enti associati', to='institutions.Institution')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.user')),
            ],
        ),
    ]
