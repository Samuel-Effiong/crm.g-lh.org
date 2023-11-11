# Generated by Django 4.2.6 on 2023-10-30 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0003_alter_department_members_names_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='department_name',
            field=models.CharField(choices=[('GMT', 'GMT'), ('Extraction', 'Extraction Team'), ('Website', 'Website Team'), ('Archive', 'Archive')], max_length=255),
        ),
    ]
