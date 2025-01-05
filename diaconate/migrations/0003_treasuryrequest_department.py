# Generated by Django 4.2.7 on 2024-08-18 21:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0069_alter_departmentproject_department_category'),
        ('diaconate', '0002_rename_resourcerequest_treasuryrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='treasuryrequest',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project_management.department'),
        ),
    ]