# Generated by Django 4.2.7 on 2024-01-14 07:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_alter_customuser_blood_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='weekthree',
            name='exception',
        ),
    ]
