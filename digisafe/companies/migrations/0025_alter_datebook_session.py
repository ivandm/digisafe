# Generated by Django 4.0.4 on 2022-05-04 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0024_alter_datebook_session'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datebook',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.sessionbook'),
        ),
    ]