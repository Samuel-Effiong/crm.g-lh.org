# Generated by Django 5.1.6 on 2025-03-22 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unperplexed', '0004_worker_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='project_duration',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
