import re
import string
import datetime
import numpy as np

from django.db import models
from django.shortcuts import reverse
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .utilities import Validators, ValidationError, get_user_name

from wagtail.snippets.models import register_snippet

SEX_CHOICES = (
    ('M', "Male"),
    ('F', "Female")
)


BLOOD_GROUP_CHOICES = (
    ('-', 'Unknown'),
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-')
)


GENOTYPE_CHOICES = (
    ('-', 'Unknown'),
    ('AA', 'AA'),
    ('AB', 'AB'),
    ('AO', 'AO'),
    ('BB', 'BB'),
    ('BO', 'BO'),
    ('OO', 'OO'),
    ('AS', 'AS'),
    ('SS', 'SS')
)

LEVEL_CHOICES = (
    ('new_mem', 'New Member'),
    ('mem', 'Member'),
    ('worker', 'Worker'),
    ('sub_shep', 'Sub Shepherd'),
    ('core_shep', 'Core Shepherd'),
    ('chief_shep', 'Chief Shepherd')
)


STRICT_REPORT = (
    ('None', 'None'),
    ('mon', 'Monday'),
    ('tue', 'Tuesday'),
    ('wed', 'Wednessday'),
    ('thur', 'Thursday'),
    ('fri', 'Friday'),
    ('sat', 'Saturday'),
    ('sun', 'Sunday')
)


GRADUATE_STATUS_CHOICES = (
    ('undergraduate', 'Undergraduate'),
    ('graduate', 'Graduate'),
)


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, save=True, **extra_fields):
        """Create and save a user with the given email and password"""
        if not email:
            raise ValueError(_("The email must be set"))

        if 'date_of_birth' in extra_fields:
            dob = extra_fields['date_of_birth']
            Validators.validate_prevent_future_date(dob)

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        if save:
            user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a super user with the given email and password"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True"))

        return self.create_user(email, password, **extra_fields)

    def get_shepherd_sheep(self, shepherd):
        """
        Returns the users who have this user as their shepherd
        """
        return self.get_queryset().filter(shepherd=shepherd)

    def get_sub_shepherd_sheep(self, sub_shepherd):
        """
        Return the users who have this user as their sub shepherd
        """
        return self.get_queryset().filter(sub_shepherd=sub_shepherd)

    def get_today_birthday(self):
        """
        Return all the users whose birthday is today
        """
        today = datetime.date.today()
        celebrants = self.get_queryset().filter(date_of_birth__month=today.month, date_of_birth__day=today.day)

        return celebrants

    def get_skills_categories_count(self):
        """Return the unique skill of the users and it counts"""
        users = self.get_queryset().exclude(level='chief_shep')

        # Remove those who have no skills or haven't entered their skills
        users_with_skills = [user for user in users if user.skills is not None and user.skills.strip()]

        users_without_skills = len(users) - len(users_with_skills)

        user_skills_list = []
        unique_skills = []

        for person in users_with_skills:
            skills = [item.strip() for item in re.split("[;,]", person.skills)]
            # remove any additional empty item that is inserted as a result of user entering double comma
            skills = [item.lower() for item in skills if item.strip()]
            skills = [re.sub(f"[{string.punctuation}]", "", item) for item in skills]

            user_skills_list.extend(skills)

        unique_skills, unique_count = np.unique(user_skills_list, return_counts=True)

        total = sum(unique_count)
        unique_percentage = [round((skill * 100) / total) for skill in unique_count]

        return unique_skills, unique_count, unique_percentage, len(users_with_skills), users_without_skills

    def get_particular_field_value_only(self, field, value):
        """Retrieve from the database the user that for a particular
        field contains the specified value"""

        items = self.get_queryset().exclude(level='chief_shep')
        if field == 'gender':
            items = items.filter(gender=value)
        elif field == 'skills':
            if value == 'None':
                items = items.filter(skills=None)
            else:
                if '__and__' in value:
                    value = value.replace('__and__', '/')
                items = items.filter(skills__icontains=value)

        else:
            raise ValueError("Must provide a value field, function won't be used as a substitute for .all() function")
        items = items.order_by('date_of_birth')
        items_list = []

        for person in items:
            full_name = person.get_full_name()
            username = person.username
            age = person.get_user_age()
            shepherd = person.shepherd.name.username if person.shepherd else 'None'

            items_list.append({
                'full_name': full_name, 'age': age,
                'chief_shepherd_access_profile_url': reverse('pastoring:sheep-profile', args=[shepherd, username])
            })

        return items_list

    def get_user_from_full_name(self, full_name):
        full_name, username = full_name.split('@')

        full_name = full_name.split()
        full_name = [valid.strip() for valid in full_name if valid]

        return self.get_queryset().get(username__iexact=username)


class CustomUser(AbstractUser):

    # BIO DATA
    first_name = models.CharField(_('First Name'), max_length=100)
    last_name = models.CharField(_('Last Name'), max_length=100)
    username = models.CharField(_('Username'), max_length=100, unique=True)
    gender = models.CharField(_('Gender'), max_length=2, choices=SEX_CHOICES)
    date_of_birth = models.DateField(_("Date of Birth"), blank=True, null=True,
                                     validators=[Validators.validate_prevent_future_date])
    about = models.TextField(_("About"), blank=True, null=True)
    profile_pic = models.FileField(_("Profile pic"), upload_to=get_user_name, blank=True)

    # PERSONAL DATA
    phone_number = models.CharField(_("Phone Number"), max_length=20)
    email = models.EmailField(_("Email address"), unique=True)
    occupation = models.CharField(_('Occupation'), max_length=100, blank=True, null=True)
    address = models.TextField(_("Address"), blank=True, null=True)
    skills = models.TextField(_('Skills'), blank=True, null=True)

    # BASIC MEDICAL INFORMATION
    blood_group = models.CharField(_("Blood Group"), max_length=10, choices=BLOOD_GROUP_CHOICES)
    genotype = models.CharField(_("Genotype"), max_length=10, choices=GENOTYPE_CHOICES)
    chronic_illness = models.CharField(_("Any Chronic Ailment"), max_length=200, help_text="please specify", blank=True, null=True)

    # RESIDENTIAL INFORMATION
    lga = models.CharField(_("LGA"), max_length=300, blank=True, null=True)
    state = models.CharField(_("State"), max_length=100, blank=True, null=True)
    country = models.CharField(_("Country"), max_length=100, blank=True, null=True)

    # SCHOOL INFORMATION
    course_of_study = models.CharField(_("Course of Study"), max_length=255, blank=True, null=True)
    years_of_study = models.CharField(_("No of Years of Study"), max_length=20, blank=True, null=True)
    current_year_of_study = models.CharField(_("Current Year of Study"), max_length=20, blank=True, null=True)
    final_year_status = models.CharField(_("Final Year Status"), max_length=255, help_text=_("Update when appropriate"), blank=True, null=True)
    graduate_status = models.CharField(_("Graduate Status"), max_length=15, choices=GRADUATE_STATUS_CHOICES, blank=True, null=True)

    # NEXT OF KIN INFORMATION
    next_of_kin_full_name = models.CharField(_('Full Name'), max_length=200, blank=True, null=True)
    next_of_kin_relationship = models.CharField(_('Relationship'), max_length=200, blank=True, null=True)
    next_of_kin_phone_number = models.CharField(_('Phone Number'), max_length=20, blank=True, null=True)
    next_of_kin_address = models.CharField(_('Address'), max_length=500, blank=True, null=True)

    # SPIRITUAL INFORMATION
    gift_graces = models.CharField(_("Gift & Graces"), max_length=500, blank=True, null=True)
    callings = models.CharField(_("Callings"), max_length=500, blank=True, null=True)
    reveal_calling_by_shepherd = models.BooleanField(_("Reveal Calling to Sheep"), default=False)

    # ADDITIONAL INFORMATION
    unit_of_work = models.CharField(_("Unit of Work"), max_length=200, blank=True, null=True)
    shepherd = models.ForeignKey('Shepherd', on_delete=models.SET_NULL, blank=True, null=True)
    sub_shepherd = models.ForeignKey('SubShepherd', on_delete=models.SET_NULL, blank=True, null=True)

    last_active_date = models.DateField(_("Last active date"), default=timezone.now)

    # SPECIAL KNOWLEDGE
    shoe_size = models.CharField(_("Shoe Size"), max_length=20, blank=True, null=True)
    cloth_size = models.CharField(_("Cloth Size"), max_length=20, blank=True, null=True)
    level = models.CharField(_('Level'), max_length=15, default='new_mem', choices=LEVEL_CHOICES)

    strict_report = models.CharField(max_length=20, default='None', choices=STRICT_REPORT)

    # checks if status is updated
    profile_updated = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} @{self.username}"

    class Meta:
        ordering = ('first_name', )
        verbose_name = "User"
        verbose_name_plural = "Users"

    @admin.display(ordering='date_of_birth', description="Age")
    def get_user_age(self):
        if self.date_of_birth:
            now = datetime.datetime.now()
            current_age = now.year - self.date_of_birth.year

            return current_age
        return None

    def set_date_of_birth(self, dob):
        dob = Validators.validate_prevent_future_date(value=dob)

        self.date_of_birth = dob

    def get_iso_date_of_birth(self):
        return self.date_of_birth.isoformat()

    def __validate_leader_roles__(self, leader, role=None):
        if role is None:
            print("I will assume leader is a shepherd")
        user_full_name = self.__str__()

        if role is None:
            leader_full_name = leader.get_shepherd_full_name()
        else:
            leader_full_name = leader.get_subshepherd_full_name()

        if user_full_name == leader_full_name:
            raise ValidationError(f"User can't be a {'Shepherd' if role is None else 'Sub Shepherd'} to himself")

    def set_shepherd(self, shepherd):
        self.__validate_leader_roles__(shepherd)
        self.shepherd = shepherd

    def set_subshepherd(self, sub_shepherd):
        """Set a user subshepherd"""
        self.__validate_leader_roles__(sub_shepherd, 'sub')
        self.sub_shepherd = sub_shepherd

    def is_birthday(self) -> bool:
        """Check if today is the user birthday and returns True"""
        if self.date_of_birth:
            today = datetime.date.today()

            day = today.day
            month = today.month

            if self.date_of_birth.day == day and self.date_of_birth.month == month:
                return True
        return False

    def get_skillset(self) -> list:
        return [skill for skill in self.skills.split(',') if skill]

    def get_image_url(self) -> str:
        if self.profile_pic:
            return self.profile_pic.url
        return ""

    def set_profile_update_status(self):
        if (self.first_name and self.last_name and self.username and 
            self.gender and self.gender and self.date_of_birth and 
            self.about and self.profile_pic and self.phone_number and
            self.email and self.occupation and self.address and 
            self.skills and self.blood_group and self.genotype and
            self.chronic_illness and self.lga and self.state and 
            self.country and self.course_of_study and self.years_of_study
            and self.current_year_of_study and self.final_year_status
            and self.next_of_kin_full_name and self.next_of_kin_relationship
            and self.next_of_kin_phone_number and self.next_of_kin_address
            and self.gift_graces and self.unit_of_work and self.shepherd
            and self.sub_shepherd and self.shoe_size and self.cloth_size
        ):
            self.profile_updated = True 

        else:
            self.profile_updated = False

    def to_dict(self):
        data = {
            'first_name': self.first_name,
            'surname': self.last_name,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth.isoformat(),
            'phone_number': self.phone_number,
            'about': self.about,
            'email': self.email,
            'occupation': self.occupation,
            'address': self.address,
            'skills': self.skills,
            'blood_group': self.blood_group,
            'genotype': self.genotype,
            'chronic_illness': self.chronic_illness,

            'lga': self.lga, 'state': self.state, 'country': self.country,

            'course_of_study': self.course_of_study,
            'years_of_study': self.years_of_study,
            'current_year_of_study': self.current_year_of_study,
            'final_year_status': self.final_year_status,
            'graduate_status': self.graduate_status,

            'next_of_kin_full_name': self.next_of_kin_full_name,
            'next_of_kin_relationship': self.next_of_kin_relationship,
            'next_of_kin_phone_number': self.next_of_kin_phone_number,
            'next_of_kin_address': self.next_of_kin_address,

            'gift_graces': self.gift_graces, 'unit_of_work': self.unit_of_work,
            'shepherd': self.shepherd if self.shepherd else "",
            'sub_shepherd': self.sub_shepherd if self.shepherd else "",

            'shoe_size': self.shoe_size, 'cloth_size': self.cloth_size,
        }
        return data


class Permission(models.Model):
    name = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, to_field='username')
    can_edit_catalog = models.BooleanField(default=False)
    head_of_department = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


@register_snippet
class FamilyMemberWeeklySchedule(models.Model):
    username = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, to_field='username', primary_key=True)

    def __str__(self):
        return f"Weekly Schedule for: {str(self.username)}"


OUT_CHOICES = (
    (None, 'None'),
    ('annex', 'Annex/Street'),
    ('permsite', 'Permsite/Street'),
    ('work_online', 'Work/Online Evangelism')
)


@register_snippet
# Create your models here.
class WeekOne(models.Model):
    family_schedule = models.OneToOneField(FamilyMemberWeeklySchedule, on_delete=models.CASCADE, to_field='username')
    In = models.BooleanField(default=False)
    out = models.CharField(max_length=25, choices=OUT_CHOICES, null=True, blank=True)
    wednesday = models.BooleanField(default=False)
    exception = models.BooleanField(default=False)

    def __str__(self):
        return f"Week One for {self.family_schedule.username.get_full_name()}"

    def get_summary(self):

        if self.In:
            return f"IN; WEDNESDAY: {self.wednesday}; EXCEPTION: {self.exception}"
        else:
            return f"{self.out}; WEDNESDAY: {self.wednesday}; EXCEPTIO: {self.exception}"

    class Meta:
        verbose_name_plural = 'Week One'


@register_snippet
class WeekTwo(models.Model):
    family_schedule = models.OneToOneField(FamilyMemberWeeklySchedule, on_delete=models.CASCADE, to_field='username')
    In = models.BooleanField(default=False)
    out = models.CharField(max_length=25, choices=OUT_CHOICES, null=True, blank=True)
    wednesday = models.BooleanField(default=False)
    exception = models.BooleanField(default=False)

    def __str__(self):
        return f"Week Two for {self.family_schedule.username.get_full_name()}"

    def get_summary(self):

        if self.In:
            return f"IN; WEDNESDAY: {self.wednesday}; EXCEPTION: {self.exception}"
        else:
            return f"{self.out}; WEDNESDAY: {self.wednesday}; EXCEPTION: {self.exception}"

    class Meta:
        verbose_name_plural = 'Week Two'


@register_snippet
class WeekThree(models.Model):
    family_schedule = models.OneToOneField(FamilyMemberWeeklySchedule, on_delete=models.CASCADE, to_field='username')
    In = models.BooleanField(default=False)
    out = models.CharField(max_length=25, choices=OUT_CHOICES, null=True, blank=True)
    wednesday = models.BooleanField(default=False)
    exception = models.BooleanField(default=False)

    def __str__(self):
        return f"Week Three for {self.family_schedule.username.get_full_name()}"

    def get_summary(self):

        if self.In:
            return f"IN; WEDNESDAY: {self.wednesday}; EXCEPTION: {self.exception}"
        else:
            return f"{self.out}; WEDNESDAY: {self.wednesday}; EXCEPTION: {self.exception}"

    class Meta:
        verbose_name_plural = 'Week Three'


@register_snippet
class WeekFour(models.Model):
    family_schedule = models.OneToOneField(FamilyMemberWeeklySchedule, on_delete=models.CASCADE, to_field='username')
    In = models.BooleanField(default=False)
    out = models.CharField(max_length=25, choices=OUT_CHOICES, null=True, blank=True)
    wednesday = models.BooleanField(default=False)
    exception = models.BooleanField(default=False)

    def __str__(self):
        return f"Week Four for {self.family_schedule.username.get_full_name()}"

    def get_summary(self):

        if self.In:
            return f"IN; WEDNESDAY: {self.wednesday}; EXCEPTION: {self.exception}"
        else:
            return f"{self.out}; WEDNESDAY: {self.wednesday}; EXCEPTION: {self.exception}"

    class Meta:
        verbose_name_plural = 'Week Four'
