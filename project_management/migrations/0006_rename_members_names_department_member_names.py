# Generated by Django 4.2.6 on 2023-10-30 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0005_alter_department_sub_leader'),
    ]

    operations = [
        migrations.RenameField(
            model_name='department',
            old_name='members_names',
            new_name='member_names',
        ),
    ]