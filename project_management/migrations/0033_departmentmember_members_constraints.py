# Generated by Django 4.2.7 on 2023-11-11 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0032_remove_departmentmember_love'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='departmentmember',
            constraint=models.UniqueConstraint(fields=('member_name', 'department_name'), name='members_constraints'),
        ),
    ]