# Generated by Django 4.2.6 on 2023-10-31 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0021_departmentproject_project_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='departmentproject',
            name='project_priority',
            field=models.CharField(blank=True, choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='departmentproject',
            name='status',
            field=models.CharField(blank=True, choices=[('In Progress', 'In Progress'), ('Completed', 'Completed'), ('Not Started', 'Not Started')], max_length=50, null=True),
        ),
    ]