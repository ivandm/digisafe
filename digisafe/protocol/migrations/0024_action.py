# Generated by Django 4.0 on 2022-01-02 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0038_auto_20220101_1835'),
        ('protocol', '0023_delete_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(default='', max_length=255)),
                ('owner', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='users.user')),
                ('protocol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='protocol.protocol')),
            ],
        ),
    ]
