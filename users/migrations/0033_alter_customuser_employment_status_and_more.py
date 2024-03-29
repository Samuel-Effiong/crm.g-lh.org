# Generated by Django 4.2.7 on 2024-02-17 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0032_skill'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='employment_status',
            field=models.CharField(blank=True, choices=[('Employed', 'Employed'), ('Employed but still looking for another job', 'Employed but still looking for another job'), ('Under Employed', 'Under Employed'), ('Unemployed', 'Unemployed')], max_length=50, null=True, verbose_name='Employment Status'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='graduate_status',
            field=models.CharField(blank=True, choices=[('None', 'None'), ('Undergraduate', 'Undergraduate'), ('Graduate', 'Graduate')], max_length=15, null=True, verbose_name='Graduate Status'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='marital_status',
            field=models.CharField(blank=True, choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widow', 'Widow')], max_length=10, null=True, verbose_name='Marital Status'),
        ),
    ]
