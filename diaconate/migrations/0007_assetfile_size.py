# Generated by Django 4.2.7 on 2024-09-14 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diaconate', '0006_assetfile_remove_asset_image_asset_files'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetfile',
            name='size',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
