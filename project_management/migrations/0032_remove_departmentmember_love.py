# Generated by Django 4.2.7 on 2023-11-11 08:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0031_departmentmember_love'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='departmentmember',
            name='love',
        ),
    ]
