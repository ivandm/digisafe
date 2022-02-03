# Generated by Django 3.2.7 on 2021-12-08 10:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('countries', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Citie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Countrie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255)),
                ('countrie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='countries.countrie')),
            ],
        ),
        migrations.RemoveField(
            model_name='states',
            name='countrie',
        ),
        migrations.DeleteModel(
            name='Cities',
        ),
        migrations.DeleteModel(
            name='Countries',
        ),
        migrations.DeleteModel(
            name='States',
        ),
        migrations.AddField(
            model_name='citie',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='countries.state'),
        ),
    ]
