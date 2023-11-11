# Generated by Django 4.2.6 on 2023-10-27 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pastoring', '0005_blogindexpage_blogpage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogpage',
            name='page_ptr',
        ),
        migrations.AddField(
            model_name='sermon',
            name='series_title',
            field=models.CharField(help_text='The Series the sermon belongs to if it is not single', max_length=1000, null=True),
        ),
        migrations.DeleteModel(
            name='BlogIndexPage',
        ),
        migrations.DeleteModel(
            name='BlogPage',
        ),
    ]