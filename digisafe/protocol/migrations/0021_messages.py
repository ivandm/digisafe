# Generated by Django 4.0 on 2022-01-02 09:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0038_auto_20220101_1835'),
        ('protocol', '0020_protocol_center'),
    ]

    operations = [
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user')),
                ('protocol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='protocol.protocol')),
            ],
        ),
    ]
