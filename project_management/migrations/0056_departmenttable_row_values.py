# Generated by Django 4.2.7 on 2023-12-05 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0055_fieldvalueindex'),
    ]

    operations = [
        migrations.AddField(
            model_name='departmenttable',
            name='row_values',
            field=models.ManyToManyField(blank=True, to='project_management.fieldvalueindex'),
        ),
    ]