# Generated by Django 4.0.4 on 2022-06-04 16:08

import companies.models
import digisafe.storage
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import maps.gisfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('countries', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('job', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('active', models.BooleanField(default=True)),
                ('admins', models.ManyToManyField(blank=True, related_name='admins_company', to=settings.AUTH_USER_MODEL)),
                ('associates', models.ManyToManyField(blank=True, related_name='associates_company', to=settings.AUTH_USER_MODEL)),
                ('favorite', models.ManyToManyField(blank=True, related_name='favorite_company', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SessionBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('city', maps.gisfields.PointField(srid=4326)),
                ('note', models.TextField(blank=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('expire_date', models.DateTimeField()),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company')),
                ('jobs', models.ManyToManyField(to='job.job')),
                ('user_decline_list', models.ManyToManyField(blank=True, related_name='sessionbook_user_decline', to=settings.AUTH_USER_MODEL)),
                ('user_option_list', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='requestAssociatePending',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_req', models.BooleanField(default=False)),
                ('company_req', models.BooleanField(default=False)),
                ('company', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='companies.company')),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255)),
                ('desc', models.TextField(default='', verbose_name='description')),
                ('logo', models.FileField(storage=digisafe.storage.FileSystemStorage(base_url='/imgs', location='static/imgs/'), upload_to=companies.models.file_path_name_company, validators=[digisafe.storage.validate_file_size, digisafe.storage.validate_file_extension_img])),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='countries.city', verbose_name='city')),
                ('company', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='companies.company')),
                ('country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='countries.country', verbose_name='country')),
            ],
        ),
        migrations.CreateModel(
            name='DateBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_user', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0)])),
                ('date', models.DateField()),
                ('user_note', models.CharField(blank=True, max_length=255, null=True)),
                ('company_note', models.CharField(blank=True, max_length=255)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_datebook', to='job.job')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datebook_set', to='companies.sessionbook')),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
                ('users_confirm', models.ManyToManyField(blank=True, related_name='datebook_confirm', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
