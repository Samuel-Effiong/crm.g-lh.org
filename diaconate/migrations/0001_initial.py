# Generated by Django 4.2.7 on 2024-08-18 21:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(verbose_name='Description|Configuration')),
                ('purchase_date', models.DateField(verbose_name='Date of Acquisition')),
                ('location', models.CharField(max_length=100)),
                ('condition', models.CharField(choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Bad But In Use', 'Bad But In Use'), ('Bad But Can Be Fixed', 'Bad But Can Be Fixed'), ('Bad and Out of Use', 'Bad and Out of Use'), ('Very Bad', 'Very Bad')], help_text='These choices represent the condition of assets, allowing for clear categorization.', max_length=50)),
                ('source_of_item', models.CharField(choices=[('Co-ownership', 'Co-ownership'), ('Gift|Donation', 'Gift|Donation'), ('Purchase', 'Purchase')], max_length=50)),
                ('image', models.ImageField(blank=True, null=True, upload_to='assets/')),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Under Maintenance', 'Under Maintenance'), ('Disposed', 'Disposed')], default='Active', help_text='These choices can be used to indicate the current status of assets or requests.', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='AssetCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('Acquisition', 'Acquisition'), ('Disposal', 'Disposal'), ('Transfer', 'Transfer')], max_length=20)),
                ('transaction_date', models.DateField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diaconate.asset')),
            ],
        ),
        migrations.CreateModel(
            name='ResourceRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_date', models.DateField(auto_now_add=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Completed', 'Completed')], default='Pending', help_text='These choices are specifically for the status of resource requests.', max_length=20)),
                ('reason', models.TextField()),
                ('approved_date', models.DateField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_requests', to=settings.AUTH_USER_MODEL)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diaconate.asset')),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(max_length=50)),
                ('generated_date', models.DateField(auto_now_add=True)),
                ('description', models.TextField()),
                ('generated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MaintenanceSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_date', models.DateField()),
                ('maintenance_type', models.CharField(max_length=100)),
                ('service_provider', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Under Maintenance', 'Under Maintenance'), ('Disposed', 'Disposed')], default='Scheduled', max_length=20)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diaconate.asset')),
            ],
        ),
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audit_id', models.CharField(max_length=20, unique=True)),
                ('audit_date', models.DateField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('auditor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='asset',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diaconate.assetcategory'),
        ),
    ]
