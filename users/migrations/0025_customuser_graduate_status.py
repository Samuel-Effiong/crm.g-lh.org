# Generated by Django 4.2.7 on 2023-12-09 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_customuser_profile_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='graduate_status',
            field=models.CharField(choices=[('none', 'None'), ('undergraduate', 'Undergraduate'), ('graduate', 'Graduate')], default='undergraduate', max_length=15, verbose_name='Graduate Status'),
            preserve_default=False,
        ),
    ]
