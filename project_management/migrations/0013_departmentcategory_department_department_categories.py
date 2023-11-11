# Generated by Django 4.2.6 on 2023-10-31 11:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0012_alter_department_member_names'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepartmentCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=255)),
                ('department_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project_management.department')),
            ],
            options={
                'verbose_name_plural': 'Department Categories',
            },
        ),
        migrations.AddField(
            model_name='department',
            name='department_categories',
            field=models.ManyToManyField(blank=True, to='project_management.departmentcategory'),
        ),
    ]
