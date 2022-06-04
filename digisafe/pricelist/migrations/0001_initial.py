# Generated by Django 4.0.4 on 2022-06-04 16:08

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields
import djmoney.models.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PriceList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('price_currency', djmoney.models.fields.CurrencyField(choices=[('EUR', 'EUR €'), ('GBP', 'GBP £'), ('USD', 'USD $')], default='USD', editable=False, max_length=3)),
                ('price', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0.0'), default_currency='USD', max_digits=7, validators=[djmoney.models.validators.MinMoneyValidator(0), djmoney.models.validators.MaxMoneyValidator(99999)])),
                ('slot_time', models.CharField(choices=[('HOUR', 'every Hour'), ('DAY', 'every Day'), ('SESSION', 'every Session')], default='HOUR', max_length=8)),
                ('note', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SessionPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_metadata', models.JSONField(default=dict)),
                ('price', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pricelist.pricelist')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.sessionbook')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExtraPriceList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('qta', models.DecimalField(decimal_places=2, max_digits=7)),
                ('unit', models.CharField(choices=[('PERC', '%'), ('MONEY', 'Money')], default='PERC', max_length=8)),
                ('add_minus', models.CharField(choices=[('add', '+'), ('minus', '-'), ('incluse', 'Incluse')], default='add', max_length=8)),
                ('pricelist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pricelist.pricelist')),
            ],
        ),
    ]
