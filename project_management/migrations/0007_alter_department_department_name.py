# Generated by Django 4.2.6 on 2023-10-30 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0006_rename_members_names_department_member_names'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='department_name',
            field=models.CharField(choices=[('GMT', 'GMT'), ('Extraction', 'Extraction Team'), ('Website', 'Website Team'), ('Archive', 'Archive')], max_length=255, unique=True),
        ),
    ]
