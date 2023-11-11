# Generated by Django 4.2.6 on 2023-11-05 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0026_projecttarget_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projecttarget',
            name='completed',
        ),
        migrations.AddField(
            model_name='projecttarget',
            name='state',
            field=models.CharField(choices=[('Not Started', 'Not Started'), ('Pending', 'Pending'), ('Completed', 'Completed')], default='Not Started', max_length=15),
        ),
    ]