# Generated by Django 4.2.7 on 2023-11-22 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0043_alter_department_leader_alter_department_sub_leader'),
    ]

    operations = [
        migrations.AlterField(
            model_name='departmentproject',
            name='project_priority',
            field=models.CharField(choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], default='Low', max_length=50),
        ),
    ]