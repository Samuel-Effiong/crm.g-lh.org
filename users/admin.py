from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (CustomUser, Shepherd, SubShepherd, Catalog, Permission,
                     FamilyMemberWeeklySchedule, WeekOne, WeekTwo, WeekThree, WeekFour)


class PermissionInline(admin.StackedInline):
    model = Permission
    can_delete = False
    verbose_name_plural = 'Permission'
    verbose_name = 'Additional Permission'


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('get_full_name', 'level', 'shepherd', 'sub_shepherd', 'get_user_age')
    list_filter = ('gender', 'country', 'state', 'lga', 'course_of_study', 'occupation', 'skills')
    search_fields = ('first_name', 'last_name', 'country', 'state', 'shepherd')
    date_hierarchy = 'date_of_birth'
    # inlines = (PermissionInline, )

    fieldsets = [
        ("Bio Data", {
            'classes': ('wide', ),
            'fields': ('first_name', 'last_name', 'username', 'gender', 'date_of_birth',
                       'about', 'password')}),
        ('Personal Data', {
            'fields': ('phone_number', 'email', 'occupation', 'address', 'skills'),
            'classes': ('wide',)
        }),
        ("Basic Medical Information", {
            'fields': ('blood_group', 'genotype', 'chronic_illness', ),
            'classes': ('collapse',)
        }),
        ("Residential Information", {
            'fields': ('lga', 'state', 'country',),
            'classes': ('collapse',)
        }),
        ("School Information", {
            'fields': ('course_of_study', 'years_of_study', 'final_year_status',),
            'classes': ('collapse',)
        }),
        ("Next of Kin", {
            'fields': ('next_of_kin_full_name', 'next_of_kin_relationship',
                       'next_of_kin_phone_number', 'next_of_kin_address', ),
            'classes': ('collapse',)
        }),
        ("Spiritual Information", {
            'fields': ('gift_graces', ('callings', 'reveal_calling_by_shepherd')),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('unit_of_work', 'shepherd', 'sub_shepherd', 'profile_pic', 'last_active_date'),
            'classes': ('collapse',)
        }),
        ('Special Knowledge', {
            'fields': ('shoe_size', 'cloth_size', 'level'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ['is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions']
        })
    ]

    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('email', 'password1', 'password2')
        }),
        ("Bio Data", {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'username', 'gender', 'date_of_birth', 'about')}),
        ('Personal Data', {
            'fields': ('phone_number', 'occupation', 'address', 'skills'),
            'classes': ('collapse',)
        }),
        ("Residential Information", {
            'fields': ('lga', 'state', 'country',),
            'classes': ('collapse',)
        }),
        ('Next of Kin', {
            'fields': ('next_of_kin_full_name', 'next_of_kin_relationship',
                       'next_of_kin_phone_number', 'next_of_kin_address'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('shepherd', 'sub_shepherd', 'profile_pic'),
            'classes': ('collapse',)
        }),
    )
    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(Shepherd)
class ShepherdAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_shepherd_gender', 'no_of_sheep', 'calling', 'get_service_duration')
    list_filter = ('name', 'calling', 'date_of_appointment')
    date_hierarchy = 'date_of_appointment'


@admin.register(SubShepherd)
class SubShepherdAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_subshepherd_gender', 'no_of_sheep',
                    'calling', 'get_service_duration',)
    list_filter = ('calling', 'date_of_appointment')
    date_hierarchy = 'date_of_appointment'


@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'sermon_title', 'things_spoken_about')
    search_fields = ('things_spoken_about', 'sermon_title',)
    date_hierarchy = 'correct_date'


class WeekOneInline(admin.TabularInline):
    model = WeekOne
    can_delete = False
    verbose_name = 'Week 1'
    verbose_name_plural = 'Week 1'


class WeekTwoInline(admin.TabularInline):
    model = WeekTwo
    can_delete = False
    verbose_name = 'Week 2'
    verbose_name_plural = 'Week 2'


class WeekThreeInline(admin.TabularInline):
    model = WeekThree
    can_delete = False
    verbose_name = 'Week 3'
    verbose_name_plural = 'Week 3'


class WeekFourInline(admin.TabularInline):
    model = WeekFour
    can_delete = False
    verbose_name = 'Week 4'
    verbose_name_plural = 'Week 4'


@admin.register(FamilyMemberWeeklySchedule)
class FamilyMemberWeeklyScheduleAdmin(admin.ModelAdmin):
    inlines = (WeekOneInline, WeekTwoInline, WeekThreeInline, WeekFourInline, )
    list_display = ('username', )

