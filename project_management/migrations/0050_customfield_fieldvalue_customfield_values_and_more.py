# Generated by Django 4.2.7 on 2023-12-05 08:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0049_alter_departmenttable_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('field_type', models.CharField(max_length=255)),
                ('foreign_key', models.CharField(help_text='Know which other it links to', max_length=255)),
                ('conditions', models.TextField(help_text='contains code that will executed with eval')),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project_management.departmenttable')),
            ],
        ),
        migrations.CreateModel(
            name='FieldValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(help_text='use custom field definition to enforce constraints')),
                ('custom_field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project_management.customfield')),
            ],
        ),
        migrations.AddField(
            model_name='customfield',
            name='values',
            field=models.ManyToManyField(blank=True, to='project_management.fieldvalue'),
        ),
        migrations.AddField(
            model_name='departmenttable',
            name='fields',
            field=models.ManyToManyField(to='project_management.customfield'),
        ),
    ]
