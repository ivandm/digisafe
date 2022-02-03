# Generated by Django 4.0 on 2021-12-13 08:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_anagrafica_provincia_nascita_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Privilegi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direttore', models.BooleanField(default=False)),
                ('docente', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.user')),
            ],
        ),
    ]
