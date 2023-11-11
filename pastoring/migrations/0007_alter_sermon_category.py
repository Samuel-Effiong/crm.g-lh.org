# Generated by Django 4.2.6 on 2023-10-30 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pastoring', '0006_remove_blogpage_page_ptr_sermon_series_title_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sermon',
            name='category',
            field=models.CharField(choices=[('audio_series', 'Audio Sermon Series'), ('audio_single', 'Audio Single Sermons'), ('sermon_videos', 'Sermon Videos'), ('fars', 'FARS Seminar')], max_length=50),
        ),
    ]
