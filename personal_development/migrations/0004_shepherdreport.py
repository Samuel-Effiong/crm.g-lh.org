# Generated by Django 4.2.1 on 2023-07-09 15:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0020_customuser_strict_report'),
        ('personal_development', '0003_remove_prayermarathon_end_time_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShepherdReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('books_read', models.TextField(blank=True, null=True)),
                ('church_work', models.TextField(blank=True, null=True)),
                ('personal_details', models.TextField(blank=True, null=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.shepherd', to_field='name')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
    ]