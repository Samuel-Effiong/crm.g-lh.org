# Generated by Django 4.2.7 on 2024-12-28 14:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diaconate', '0009_treasuryrequest_new_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetcategory',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='diaconate.assetcategory')),
            ],
        ),
        migrations.CreateModel(
            name='AssetAttributeValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attribute_values', to='diaconate.asset')),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diaconate.attribute')),
            ],
        ),
    ]
