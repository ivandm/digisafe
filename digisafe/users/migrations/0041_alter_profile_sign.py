# Generated by Django 4.0 on 2022-01-17 10:49

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0040_profile_sign'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='sign',
            field=models.ImageField(storage=users.models.ProtocolFileSystemStorage(base_url='/signs', location='signs/'), upload_to=users.models.file_path_name, validators=[users.models.validate_file_size, users.models.validate_file_extension, users.models.validate_file_trasparence]),
        ),
    ]