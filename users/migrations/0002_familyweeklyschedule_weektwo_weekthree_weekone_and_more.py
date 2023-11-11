# Generated by Django 4.1.7 on 2023-04-04 10:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FamilyWeeklySchedule',
            fields=[
                ('username', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
        ),
        migrations.CreateModel(
            name='WeekTwo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('In', models.BooleanField(default=False)),
                ('out', models.CharField(blank=True, choices=[(None, 'None'), ('annex', 'Annex/Street'), ('permsite', 'Permsite/Street'), ('work_online', 'Work/Online Evangelism')], max_length=25, null=True)),
                ('wednesday', models.BooleanField(default=False)),
                ('exception', models.BooleanField(default=False)),
                ('family_schedule', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.familyweeklyschedule')),
                ('username', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'verbose_name_plural': 'Week Two',
            },
        ),
        migrations.CreateModel(
            name='WeekThree',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('In', models.BooleanField(default=False)),
                ('out', models.CharField(blank=True, choices=[(None, 'None'), ('annex', 'Annex/Street'), ('permsite', 'Permsite/Street'), ('work_online', 'Work/Online Evangelism')], max_length=25, null=True)),
                ('wednesday', models.BooleanField(default=False)),
                ('exception', models.BooleanField(default=False)),
                ('family_schedule', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.familyweeklyschedule')),
                ('username', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'verbose_name_plural': 'Week Three',
            },
        ),
        migrations.CreateModel(
            name='WeekOne',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('In', models.BooleanField(default=False)),
                ('out', models.CharField(blank=True, choices=[(None, 'None'), ('annex', 'Annex/Street'), ('permsite', 'Permsite/Street'), ('work_online', 'Work/Online Evangelism')], max_length=25, null=True)),
                ('wednesday', models.BooleanField(default=False)),
                ('exception', models.BooleanField(default=False)),
                ('family_schedule', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.familyweeklyschedule')),
                ('username', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'verbose_name_plural': 'Week One',
            },
        ),
        migrations.CreateModel(
            name='WeekFour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('In', models.BooleanField(default=False)),
                ('out', models.CharField(blank=True, choices=[(None, 'None'), ('annex', 'Annex/Street'), ('permsite', 'Permsite/Street'), ('work_online', 'Work/Online Evangelism')], max_length=25, null=True)),
                ('wednesday', models.BooleanField(default=False)),
                ('exception', models.BooleanField(default=False)),
                ('family_schedule', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.familyweeklyschedule')),
                ('username', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'verbose_name_plural': 'Week Four',
            },
        ),
    ]
