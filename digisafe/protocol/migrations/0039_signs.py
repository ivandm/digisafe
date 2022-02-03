# Generated by Django 4.0 on 2022-01-18 18:21

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0041_alter_profile_sign'),
        ('protocol', '0038_protocol_datetime'),
    ]

    operations = [
        migrations.CreateModel(
            name='Signs',
            fields=[
                ('uiid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField()),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='protocol.files')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='users.user')),
            ],
        ),
    ]
