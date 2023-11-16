from django.contrib import admin

from . import models


# Register your models here.
@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'leader', 'sub_leader', 'get_no_of_members', 'get_no_of_categories')


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
