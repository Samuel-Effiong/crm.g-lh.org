# Generated by Django 4.2.7 on 2024-08-10 13:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0038_permission_short_link_manager'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='name',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]