# Generated by Django 4.2.7 on 2024-03-23 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_alter_customuser_cloth_size_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='church_outpost',
            field=models.CharField(blank=True, choices=[('Port Harcourt', 'Port Harcourt'), ('Lagos', 'Lagos'), ('Ikot Ekpene', 'Ikot Ekpene'), ('Abuja', 'Abuja'), ('Enugu', 'Enugu'), ('Calabar', 'Calabar'), ('Uyo', 'Uyo'), ('None', 'None')], max_length=50, null=True, verbose_name='Church Outpost'),
        ),
    ]