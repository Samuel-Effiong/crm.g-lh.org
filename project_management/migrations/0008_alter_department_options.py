# Generated by Django 4.2.6 on 2023-10-30 16:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0007_alter_department_department_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='department',
            options={'ordering': ('department_name',)},
        ),
    ]
