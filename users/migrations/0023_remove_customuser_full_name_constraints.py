# Generated by Django 4.2.7 on 2023-11-26 22:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_customuser_full_name_constraints'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='customuser',
            name='full_name_constraints',
        ),
    ]
