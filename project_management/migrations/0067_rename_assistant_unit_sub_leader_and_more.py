# Generated by Django 4.2.7 on 2024-03-02 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0066_remove_department_department_units'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unit',
            old_name='assistant',
            new_name='sub_leader',
        ),
        migrations.RenameField(
            model_name='unit',
            old_name='head',
            new_name='unit_leader',
        ),
        migrations.AddField(
            model_name='unit',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='+', to='project_management.departmentmember'),
        ),
    ]
