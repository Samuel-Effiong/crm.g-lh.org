# Generated by Django 4.2.7 on 2024-01-19 13:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project_management', '0058_subunit_unit_name_team_sub_unit_unit_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episcopate',
            name='assistant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='episcopate',
            name='head',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='subunit',
            name='assistant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='project_management.departmentmember'),
        ),
        migrations.AlterField(
            model_name='subunit',
            name='head',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project_management.departmentmember'),
        ),
        migrations.AlterField(
            model_name='team',
            name='assistant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='project_management.departmentmember'),
        ),
        migrations.AlterField(
            model_name='team',
            name='head',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member_head', to='project_management.departmentmember'),
        ),
        migrations.AlterField(
            model_name='unit',
            name='assistant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='project_management.departmentmember'),
        ),
        migrations.AlterField(
            model_name='unit',
            name='head',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project_management.departmentmember'),
        ),
    ]
