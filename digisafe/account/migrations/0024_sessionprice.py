# Generated by Django 4.0.4 on 2022-05-17 13:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pricelist', '0009_pricelist_note'),
        ('account', '0023_delete_agenda'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pricelist.pricelist')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.sessionbook')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
