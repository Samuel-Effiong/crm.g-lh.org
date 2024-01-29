from django.contrib import admin

from . import models


# Register your models here.
@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'department_long_name', 'leader', 'sub_leader', 'get_no_of_members', 'get_no_of_categories')


@admin.register(models.DepartmentMember)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'department_name')
    list_filter = ('department_name', 'member_name')


@admin.register(models.DepartmentCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'department_name')


@admin.register(models.DepartmentProject)
class DepartmentProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'department', 'department_category',
                    'get_no_of_workers', 'project_priority', 'status',
                    'get_no_of_target')


@admin.register(models.ProjectTarget)
class TargetAdmin(admin.ModelAdmin):
    list_display = ('target_name', 'project', 'get_target_department', 'state')


@admin.register(models.PendingDepartmentRequest)
class PendingDepartmentRequestAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'target_department', 'date')
    date_hierarchy = 'date'
    list_filter = ('target_department', 'date',)


# @admin.register(models.DepartmentTable)
# class DepartmentTable(admin.ModelAdmin):
#     list_display = ('table_name', 'department', 'date')
#     list_filter = ('department',)
#     date_hierarchy = 'date'


class FieldValueInline(admin.TabularInline):
    model = models.FieldValue
    extra = 1


class CustomFieldInline(admin.ModelAdmin):
    model = models.CustomField
    inlines = [FieldValueInline]


@admin.register(models.DepartmentTable)
class DepartmentTableAdmin(admin.ModelAdmin):
    list_display = ('table_name_plural', 'department_name', 'date',)
    list_filter = ('department_name', )
    date_hierarchy = 'date'


@admin.register(models.CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'field_type', 'table')
    list_filter = ('field_type', 'table')


@admin.register(models.FieldValue)
class FieldValueAdmin(admin.ModelAdmin):
    list_display = ('value', 'custom_field')
    list_filter = ('custom_field', )


@admin.register(models.FieldValueIndex)
class FieldValueIndexAdmin(admin.ModelAdmin):
    list_display = ('department_table_name', 'id')
    list_filter = ('department_table_name', )


@admin.register(models.Diaconate)
class EpiscopateAdmin(admin.ModelAdmin):
    list_display = ('name', 'head', 'assistant', 'get_number_of_departments')


@admin.register(models.Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'head', 'assistant', 'get_number_of_subunit')


@admin.register(models.SubUnit)
class SubUnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'head', 'assistant', 'get_number_of_teams')


@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'head', 'assistant', 'get_number_of_members')
