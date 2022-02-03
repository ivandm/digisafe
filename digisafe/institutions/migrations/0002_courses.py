# Generated by Django 4.0 on 2022-01-04 16:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0017_courses_need_institution'),
        ('institutions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Courses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField(blank=True, default='')),
                ('courses', models.ManyToManyField(blank=True, help_text='Corsi gestiti', to='courses.Courses')),
                ('institution', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='institutions.institution')),
            ],
        ),
    ]
