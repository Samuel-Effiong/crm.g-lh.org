# Generated by Django 4.2.7 on 2024-09-20 21:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diaconate', '0007_assetfile_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='treasuryrequest',
            name='asset_category',
        ),
    ]