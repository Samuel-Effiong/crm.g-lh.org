# Generated by Django 4.2.7 on 2024-03-17 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_course_alter_skill_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='cloth_size',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Cloth Size'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='shoe_size',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Shoe Size'),
        ),
    ]
