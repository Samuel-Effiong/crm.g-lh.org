# Generated by Django 4.2.7 on 2024-08-05 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pastoring', '0014_alter_urlshortener_original_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='urlshortener',
            name='shortened_url',
            field=models.URLField(unique=True),
        ),
    ]
