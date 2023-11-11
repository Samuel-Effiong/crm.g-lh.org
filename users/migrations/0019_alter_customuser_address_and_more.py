# Generated by Django 4.2.1 on 2023-06-26 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_permission_name_alter_customuser_skills'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='address',
            field=models.TextField(blank=True, null=True, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='next_of_kin_relationship',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Relationship'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='skills',
            field=models.TextField(blank=True, null=True, verbose_name='Skills'),
        ),
    ]
