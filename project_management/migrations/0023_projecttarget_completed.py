# Generated by Django 4.2.6 on 2023-11-02 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0022_alter_departmentproject_project_priority_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='projecttarget',
            name='completed',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
