# Generated by Django 4.2.1 on 2023-05-23 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_alter_customuser_chronic_illness_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='permission',
            name='name',
        ),
    ]
