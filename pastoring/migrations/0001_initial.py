# Generated by Django 4.2.5 on 2023-09-27 22:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1000)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('message', models.TextField()),
                ('author', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='PropheticWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('church', 'WORDS FOR THE CHURCH'), ('nigeria', 'WORDS FOR NIGERIA'), ('season', 'WORDS FOR THE SEASON'), ('general', 'GENERAL WORDS')], max_length=50)),
                ('title', models.CharField(max_length=1000)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('speaker', models.CharField(max_length=255)),
                ('message', models.TextField()),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='Sermon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1000)),
                ('category', models.CharField(choices=[('audio_series', 'Audio Sermon Series'), ('audio_single', 'Audio Single Sermons'), ('sermon_videos', 'Sermon Videos'), ('fars', 'FARS Serminar')], max_length=50)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('download_link', models.URLField()),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='Testimony',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('testifier', models.CharField(max_length=255)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('category', models.CharField(choices=[('life', 'Life Testimony'), ('general', 'General Testimony'), ('evangelism', 'Evangelism Testimony')], max_length=50)),
                ('message', models.TextField()),
                ('title', models.CharField(max_length=1000)),
            ],
            options={
                'verbose_name_plural': 'Testimonies',
                'ordering': ('-date',),
            },
        ),
    ]
