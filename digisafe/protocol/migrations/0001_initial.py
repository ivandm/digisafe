# Generated by Django 4.0 on 2021-12-16 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('countries', '0013_rename_catasto_city_sigla_prov_city_prov'),
        ('users', '0031_rename_direttore_profile_director_and_more'),
        ('courses', '0010_remove_new_hours_remove_new_year_remove_update_hours'),
    ]

    operations = [
        migrations.CreateModel(
            name='Protocol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('new', 'New'), ('update', 'Update')], default='new', max_length=25)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.courses')),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(null=True)),
                ('start_time', models.TimeField(null=True)),
                ('end_time', models.TimeField(null=True)),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='countries.city')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='countries.country')),
                ('protocol', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='protocol.protocol')),
                ('trainer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.user')),
            ],
        ),
    ]