# Generated by Django 4.0 on 2022-01-11 18:51

from django.db import migrations, models
import institutions.models


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0005_institution_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='logo',
            field=models.FileField(blank=True, storage=institutions.models.ProtocolFileSystemStorage(base_url='/imgs', location='static/imgs/'), upload_to=institutions.models.file_path_name_institution, validators=[institutions.models.validate_file_size, institutions.models.validate_file_extension]),
        ),
    ]