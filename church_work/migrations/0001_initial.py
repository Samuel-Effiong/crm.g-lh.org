# Generated by Django 4.1.7 on 2023-03-26 23:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChurchWork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_category', models.CharField(choices=[('transcription', 'Transcription'), ('video_editing', 'Video Editing'), ('building', 'Building'), ('extraction', 'Extraction'), ('audio_editing', 'Audio Editing'), ('audio_video_review', 'Audio/Video Review'), ('audio_video_snippets', 'Audio/Video Snippets')], max_length=100)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('start_time', models.TimeField(default=django.utils.timezone.now)),
                ('end_time', models.TimeField(default=django.utils.timezone.now)),
                ('details', models.TextField()),
                ('hours_spent', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
    ]