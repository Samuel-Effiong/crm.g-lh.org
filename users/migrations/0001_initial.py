# Generated by Django 4.1.7 on 2023-04-03 12:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import users.my_models.miscellaneous
import users.my_models.utilities


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_name', models.CharField(max_length=100, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=100, verbose_name='Last Name')),
                ('username', models.CharField(max_length=100, unique=True, verbose_name='Username')),
                ('sex', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=10, verbose_name='Sex')),
                ('date_of_birth', models.DateField(blank=True, null=True, validators=[users.my_models.utilities.Validators.validate_prevent_future_date], verbose_name='Date of Birth')),
                ('about', models.TextField(blank=True, null=True, verbose_name='About')),
                ('profile_pic', models.FileField(blank=True, upload_to=users.my_models.utilities.get_user_name, verbose_name='Profile pic')),
                ('phone_number', models.CharField(max_length=20, verbose_name='Phone Number')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email address')),
                ('occupation', models.CharField(blank=True, max_length=100, null=True, verbose_name='Occupation')),
                ('address', models.CharField(max_length=500, verbose_name='Address')),
                ('skills', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Skills')),
                ('lga', models.CharField(blank=True, max_length=300, null=True, verbose_name='LGA')),
                ('state', models.CharField(blank=True, max_length=100, null=True, verbose_name='State')),
                ('country', models.CharField(blank=True, max_length=100, null=True, verbose_name='Country')),
                ('next_of_kin_full_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Full Name')),
                ('next_of_kin_relationship', models.CharField(blank=True, max_length=50, null=True, verbose_name='Relationship')),
                ('next_of_kin_phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Phone Number')),
                ('next_of_kin_address', models.CharField(blank=True, max_length=500, null=True, verbose_name='Address')),
                ('gift_graces', models.CharField(blank=True, max_length=500, null=True, verbose_name='Gift & Graces')),
                ('callings', models.CharField(blank=True, max_length=500, null=True, verbose_name='Callings')),
                ('reveal_calling_by_shepherd', models.BooleanField(default=False, verbose_name='Reveal Calling to Sheep')),
                ('unit_of_work', models.CharField(blank=True, max_length=200, null=True, verbose_name='Unit of Work')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'ordering': ('first_name',),
            },
        ),
        migrations.CreateModel(
            name='Catalog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(blank=True, max_length=201, null=True)),
                ('date', users.my_models.miscellaneous.OutdatedDateField(blank=True, max_length=30, null=True)),
                ('correct_date', models.DateField(blank=True, help_text='<span style="color:red;">Use this date field to record date instead of the above date field</span>', null=True, validators=[users.my_models.utilities.Validators.validate_prevent_future_date])),
                ('count', models.PositiveIntegerField(default=1)),
                ('sermon_title', models.CharField(blank=True, max_length=1000, null=True)),
                ('things_spoken_about', models.TextField()),
                ('new_songs_received', models.TextField(blank=True, null=True)),
                ('testimonies', models.TextField(blank=True, null=True)),
                ('recommended_books_movies', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ('correct_date',),
            },
        ),
        migrations.CreateModel(
            name='Shepherd',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_of_sheep', models.IntegerField()),
                ('date_of_appointment', models.DateField(validators=[users.my_models.utilities.Validators.validate_prevent_future_date])),
                ('calling', models.CharField(choices=[('unknown', 'Unknown'), ('apostle', 'Apostle'), ('prophet', 'Prophet'), ('evangelist', 'Evangelist'), ('teacher', 'Teacher'), ('pastor', 'Pastor')], default='unknown', max_length=15)),
                ('name', models.OneToOneField(limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'ordering': ('no_of_sheep',),
            },
        ),
        migrations.CreateModel(
            name='SubShepherd',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_of_sheep', models.IntegerField()),
                ('date_of_appointment', models.DateField(verbose_name=users.my_models.utilities.Validators.validate_prevent_future_date)),
                ('calling', models.CharField(choices=[('unknown', 'Unknown'), ('apostle', 'Apostle'), ('prophet', 'Prophet'), ('evangelist', 'Evangelist'), ('teacher', 'Teacher'), ('pastor', 'Pastor')], max_length=15)),
                ('name', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
                ('shepherd', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.shepherd', to_field='name')),
            ],
            options={
                'verbose_name': 'Sub Shepherd',
                'ordering': ('no_of_sheep',),
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_shepherd', models.BooleanField(default=False)),
                ('is_subshepherd', models.BooleanField(default=False)),
                ('can_edit_catalog', models.BooleanField(default=False)),
                ('head_of_department', models.BooleanField(default=False)),
                ('name', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
        ),
        migrations.AddField(
            model_name='customuser',
            name='shepherd',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.shepherd'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='sub_shepherd',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.subshepherd'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
