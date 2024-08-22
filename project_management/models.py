from typing import Tuple, Dict

# from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model

from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# import numpy as np
# import pandas as pd

# from users.models import Shepherd


class Utility:
    pass


class DepartmentMemberManager(models.Manager):
    def get_department_members(self, department):
        """Get all the members that belongs to a specific department"""
        members = self.get_queryset().filter(department_name=department)
        return members

    def get_user_departments(self, user):
        """Get a list of all the department a user is a member to"""
        departments_membership = self.get_queryset().filter(member_name=user)
        departments = [department.department_name for department in departments_membership]

        return departments

    def is_in_a_department(self, user):
        """Check if user is a member of any department"""
        member = self.get_queryset().filter(member_name=user)

        return len(self.get_user_departments(user)) > 0

 
# Create your models here.
class DepartmentMember(models.Model):
    """A user that is a member of a department
    """
    member_name = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    department_name = models.ForeignKey('Department', on_delete=models.CASCADE)
    experience_score = models.IntegerField(default=0)

    objects = DepartmentMemberManager()

    class Meta:
        verbose_name_plural = 'Department Members'
        constraints = [
            models.UniqueConstraint(
                fields=('member_name', 'department_name'),
                name="members_constraints"
            )
        ]

    def __str__(self) -> str:
        return f"{self.member_name.get_full_name()} - {self.department_name}"

    def get_member_image_url(self) -> str:
        return self.member_name.get_image_url()

    def get_active_projects(self):
        active_projects = DepartmentProject.objects.get_active_projects(
            department=self.department_name, member=self
        )
        return active_projects

    def get_inactive_projects(self):
        inactive_projects = DepartmentProject.objects.get_inactive_projects(
            department=self.department_name, member=self
        )
        return inactive_projects

    def get_completed_projects(self):
        completed_projects = DepartmentProject.objects.get_completed_projects(
            department=self.department_name, member=self
        )
        return completed_projects


class DepartmentCategoryManager(models.Manager):
    def get_department_categories(self, department):
        """"Get all the category that belongs to a specific department"""
        categories = self.get_queryset().filter(department_name=department)
        return categories


class DepartmentCategory(models.Model):
    category_name = models.CharField(max_length=255)
    department_name = models.ForeignKey('Department', on_delete=models.CASCADE)
    category_objective = models.TextField()

    objects = DepartmentCategoryManager()

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = 'Department Categories'
        constraints = [
            models.UniqueConstraint(
                fields=('category_name', 'department_name'),
                name="category_constraints"
            )
        ]


class DepartmentManager(models.Manager):
    def get_member_departments(self, user):
        """Get all the department a specific user is in"""
        departments = self.get_queryset().filter(member_names__member_name=user)
        return list(set(departments))

    def department_leaders(self) -> list[DepartmentMember]:
        leaders = [department.leader for department in self.get_queryset()]
        return leaders


class Department(models.Model):
    CHOICES = (
        ('GMT', 'GMT'),
        ('Extraction', 'Extraction Team'),
        ('Website', 'Website Team'),
        ('Archive', 'Archive'),
        ('GRT', 'GRT'),
    )

    member_names = models.ManyToManyField(DepartmentMember, blank=True)
    department_categories = models.ManyToManyField(DepartmentCategory, blank=True)
    department_name = models.CharField(_('Department'), max_length=255, unique=True)
    department_long_name = models.CharField(_('Department (Long Name)'), max_length=1000, null=True, blank=True)
    leader = models.ForeignKey(DepartmentMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    sub_leader = models.ForeignKey(DepartmentMember, on_delete=models.SET_NULL, blank=True, null=True, related_name='+')

    department_objectives = models.TextField(null=True, blank=True)
    custom_tables = models.ManyToManyField('DepartmentTable', blank=True)

    department_diaconate = models.ForeignKey('Diaconate', on_delete=models.CASCADE, blank=True, null=True)
    # department_units = models.ManyToManyField('Unit', blank=True)
    objects = DepartmentManager()

    constraints = [
        models.UniqueConstraint(
            fields=('department_diaconate', 'department_name'),
            name="unique_episcopate_department"
        )
    ]

    class Meta:
        ordering = ('department_name', )

    def __str__(self):
        return f"{self.department_name}\t-\t\t{self.department_diaconate}"

    @admin.display(description='No of Members')
    def get_no_of_members(self) -> int:
        members = self.member_names.all()

        if members:
            no_of_member = len(members)
            return no_of_member
        return 0

    @admin.display(description='No of Category')
    def get_no_of_categories(self) -> int:
        categories = self.department_categories.all()

        if categories:
            no_of_categories = len(categories)
            return no_of_categories
        return 0

    def department_leaders(self) -> list[DepartmentMember]:
        leaders = Department.objects.department_leaders()
        return leaders

    def is_leader(self, member: DepartmentMember) -> bool:
        return self.leader == member

    def is_member(self, member) -> bool:
        department_member = self.member_names.all().filter(member_name=member)

        if department_member:
            return True
        return False

    def member_activity_in_a_department(self):
        members = self.member_names.all()
        member_completed_project = []

        for member in members:
            completed_project = DepartmentProject.objects.get_completed_projects(self, member)
            member_completed_project.append(len(completed_project))

        return members, member_completed_project

    def get_department_project_events(self):
        all_department_projects = DepartmentProject.objects.filter(department=self)

        events = [department_project.to_event() for department_project in all_department_projects]
        return events


class ProjectTargetManager(models.Manager):
    def all_department_pending_target(self, department: Department):
        pending_target = self.get_queryset().filter(project__department=department, state='Pending Approval')
        return pending_target


class ProjectTarget(models.Model):
    Choices = (
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Pending Approval', 'Pending Approval')
    )

    target_name = models.CharField(max_length=1000)
    project = models.ForeignKey('DepartmentProject', on_delete=models.CASCADE)
    state = models.CharField(max_length=25, choices=Choices, default='Not Started')
    date = models.DateField(blank=True, null=True)

    objects = ProjectTargetManager()

    def __str__(self):
        return self.target_name

    class Meta:
        verbose_name_plural = 'Project Targets'

    @admin.display(description="Department")
    def get_target_department(self):
        return self.project.department.department_name


class DepartmentProjectManager(models.Manager):
    def get_active_projects(self, department: Department, member: DepartmentMember = None):
        """If member is None it returns all the active projects in a particular department
        else if returns the active project that the user is part of in the department
        """

        department_project = self.get_queryset().filter(department=department, status='In Progress')

        if member is None:
            return department_project
        else:
            return department_project.filter(project_members=member)

    def get_completed_projects(self, department: Department, member: DepartmentMember = None):
        """If member is None it returns all the completed projects in a particular department
        else if returns the completed project that the user is part of in the department
        """
        department_project = self.get_queryset().filter(department=department, status='Completed')

        if member is None:
            return department_project
        else:
            return department_project.filter(project_members=member)

    def get_inactive_projects(self, department: Department, member: DepartmentMember = None):
        """If member is None it returns all the inactive projects in a particular department
        else if returns the inactive project that the user is part of in the department
        """
        department_project = self.get_queryset().filter(department=department, status='Not Started')

        if member is None:
            return department_project
        else:
            return department_project.filter(project_members=member)

    def get_department_projects_status_statistic(self, department: Department):
        active_project = len(self.get_active_projects(department))
        completed_project = len(self.get_completed_projects(department))
        inactive_project = len(self.get_inactive_projects(department))

        total = active_project + completed_project + inactive_project

        if total > 0:
            active_percentage = round((active_project / total) * 100, 2)
            completed_percentage = round((completed_project / total) * 100, 2)
            inactive_percentage = round((inactive_project / total) * 100, 2)
        else:
            active_percentage, completed_percentage, inactive_percentage = 0, 0, 0

        result = {
            'active': {
                'freq': active_project,
                'percent': active_percentage
            },
            'completed': {
                'freq': completed_project,
                'percent': completed_percentage
            },
            'inactive': {
                'freq': inactive_project,
                'percent': inactive_percentage
            }
        }
        
        return result

    def calc_member_completed_percentage(self, user):
        user_departments = DepartmentMember.objects.filter(member_name=user)
        projects = self.get_queryset().filter(project_members__in=user_departments)

        targets_completed = []
        total = 0

        for project in projects:
            targets = project.target.all()
            total += len(targets)
            
            targets = targets.filter(state='Completed')
            targets_completed.extend(targets)

        try:
            percentage = ((len(targets_completed) / total) * 100, 2)
        except ZeroDivisionError:
            percentage = 0

        return percentage


class DepartmentProject(models.Model): 
    PRIORITY_CHOICES = (
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    )

    STATUS_CHOICES = (
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Not Started', 'Not Started')
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=1000, unique=True)
    project_description = models.TextField()

    department_category = models.ForeignKey(DepartmentCategory, on_delete=models.CASCADE, null=True, blank=True)
    project_members = models.ManyToManyField(DepartmentMember, blank=True)
    project_leader = models.ForeignKey(DepartmentMember, on_delete=models.CASCADE, null=True, blank=True, related_name='+')

    project_priority = models.CharField(max_length=50, default='Low', choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=50, blank=True, null=True, choices=STATUS_CHOICES)

    target = models.ManyToManyField(ProjectTarget, blank=True)

    start_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)

    # Choose colour that will be associated to the project
    project_background_color = models.CharField(max_length=100, null=True, blank=True)
    project_text_color = models.CharField(max_length=100, null=True, blank=True)

    objects = DepartmentProjectManager()

    def __str__(self) -> str:
        return self.project_name

    class Meta:
        verbose_name_plural = 'Department Projects'
        ordering = ('due_date', )

    @admin.display(description="No of Workers")
    def get_no_of_workers(self) -> int:
        project_members = self.project_members.all()

        return len(project_members)

    @admin.display(description='No of Targets')
    def get_no_of_target(self) -> int:
        target = self.target.all()
        return len(target)

    def get_complete_percentage(self) -> int:
        targets = self.target.all()

        # get targets that are completed
        completed_target = [target for target in targets if target.state == 'Completed']
        try:
            complete_percentage = int((len(completed_target) / len(targets)) * 100)
        except ZeroDivisionError:
            complete_percentage = 0

        return complete_percentage

    def any_pending_target_approval(self) -> bool:
        targets = self.target.all()

        pending_approval = False

        for target in targets:
            if target.state == 'Pending Approval':
                pending_approval = True
                break

        return pending_approval

    def update_current_status_of_project_target(self) -> None:
        """Check if all the target is completed in the project and mark the
        project as done"""

        targets = self.target.all()
        is_completed = False
        is_in_progress = False
        is_not_started = False

        for target in targets:
            if target.state == 'Completed':
                is_completed = True

                is_in_progress = False
                is_not_started = False

            elif target.state == 'In Progress':
                is_in_progress = True

                is_completed = False
                is_not_started = False

            elif target.state == 'Not Started':
                is_not_started = True

                is_completed = False
                is_in_progress = False

        if is_completed:
            self.status = 'Completed'
        elif is_in_progress:
            self.status = 'In Progress'
        else:
            self.status = 'Not Started'

        self.save()

    def to_event(self):
        group_id = self.department_category.category_name
        title = self.project_name
        start = self.start_date.isoformat()
        end = self.due_date.isoformat()
        background_color = self.project_background_color
        text_color = self.project_text_color

        event = {
            'groupId': group_id, 'title': title,
            'url': f"{self.get_absolute_url()}",
            'start': start, 'end': end,
            'backgroundColor': background_color,
            'textColor': text_color,
            'borderColor': text_color
        }

        return event

    def get_absolute_url(self):
        return reverse_lazy('project_management:project-detail', args=[self.department, self.id])


class PendingDepartmentRequest(models.Model):
    applicant = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    target_department = models.ForeignKey(Department, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    reasons = models.TextField()

    def __str__(self):
        return f"{self.applicant.get_full_name()} applied to {self.target_department}"


class DepartmentTable(models.Model):
    department_name = models.ForeignKey(Department, on_delete=models.CASCADE)
    table_name = models.CharField(max_length=100, unique=True)
    table_name_plural = models.CharField(max_length=255)
    table_description = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    fields = models.ManyToManyField('CustomField', blank=True)
    row_values = models.ManyToManyField('FieldValueIndex', blank=True)

    class Meta:
        verbose_name_plural = "Department's Tables"
        ordering = ('-date', )

    def __str__(self):
        return f"{self.table_name} by {self.department_name}"
    
    def value_counts(self):
        # select a particular field
        field = self.fields.first()

        if field and isinstance(field, CustomField):
            # check how many values this particular field have
            values = field.values.all()
            return len(values)
        else:
            return 0


class CustomField(models.Model):
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=255)
    table = models.ForeignKey(DepartmentTable, on_delete=models.CASCADE)
    foreign_key = models.CharField(max_length=255, blank=True, null=True,
                                   help_text="Know which other it links to")
    conditions = models.TextField(
        blank=True, null=True,
        help_text="contains code that will executed with eval")

    values = models.ManyToManyField('FieldValue', blank=True)

    def __str__(self):
        return f"{self.name}, Table: {self.table.table_name}"


class FieldValueIndex(models.Model):
    """This model is basically saying "Hey for each row this table
    has this values" 
    
    """
    department_table_name = models.ForeignKey(DepartmentTable, on_delete=models.CASCADE)
    table_field_value = models.ManyToManyField('FieldValue', blank=True)

    def __str__(self):
        return f"{self.department_table_name}, row number: {self.pk}"
    
    def to_dict(self):
        values = {item.custom_field.name: item.value for item in self.table_field_value.all() }

        return values


class FieldValue(models.Model):
    value = models.TextField(
        blank=True, null=True,
        help_text="use custom field definition to enforce constraints")
    
    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE)

    def __str__(self):
        return f"Field: {self.custom_field.name}, Value: {self.value}"


class CustomDiaconateManager(models.Manager):
    pass


class Diaconate(models.Model):
    name = models.CharField(max_length=500, unique=True)
    info = models.TextField(null=True, blank=True)
    head = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    assistant = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    departments = models.ManyToManyField(Department, blank=True)
    objects = CustomDiaconateManager()

    def __str__(self):
        return f"{self.name}"

    @admin.display(description="Number of Departments")
    def get_number_of_departments(self) -> int:
        return self.departments.count()


class CustomUnitManager(models.Manager):
    pass


class Unit(models.Model):
    name = models.CharField(max_length=500)
    objective = models.TextField(null=True, blank=True)
    unit_leader = models.ForeignKey(DepartmentMember, on_delete=models.SET_NULL, null=True, blank=True)
    sub_leader = models.ForeignKey(DepartmentMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    members = models.ManyToManyField(DepartmentMember, blank=True, related_name='+')

    unit_department = models.ForeignKey(Department, on_delete=models.CASCADE)
    sub_units = models.ManyToManyField('SubUnit', blank=True)
    objects = CustomUnitManager()

    constraints = [
        models.UniqueConstraint(
            fields=('unit_department', 'name'),
            name='unique_department_unit'
        )
    ]

    def __str__(self):
        return f"{self.name}\t-\t\t{self.unit_department}"

    @admin.display(description="Number of Sub Units")
    def get_number_of_subunit(self):
        return self.sub_units.count()
    
    def get_number_of_unit_members(self):
        return self.members.count()


class SubUnitManager(models.Manager):
    pass


class SubUnit(models.Model):
    name = models.CharField(max_length=500)
    info = models.TextField(null=True, blank=True)
    head = models.ForeignKey(DepartmentMember, on_delete=models.SET_NULL, null=True, blank=True)
    assistant = models.ForeignKey(DepartmentMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    unit_name = models.ForeignKey(Unit, on_delete=models.CASCADE)
    teams = models.ManyToManyField('Team', blank=True)
    objects = SubUnitManager()

    constraint = [
        models.UniqueConstraint(
            fields=('unit_name', name),
            name='unique_unit_sub_unit'
        )
    ]

    def __str__(self):
        return f"{self.name}\t-\t\t{self.unit_name}"

    @admin.display(description="Number of Teams")
    def get_number_of_teams(self):
        return self.teams.count()


class TeamManager(models.Manager):
    pass


class Team(models.Model):
    name = models.CharField(max_length=500)
    info = models.TextField(null=True, blank=True)
    head = models.ForeignKey(DepartmentMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='member_head')
    assistant = models.ForeignKey(DepartmentMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    sub_unit = models.ForeignKey(SubUnit, on_delete=models.CASCADE)
    members = models.ManyToManyField(DepartmentMember, blank=True)
    objects = TeamManager()

    constraint = [
        models.UniqueConstraint(
            fields=('sub_unit', 'name'),
            name="unique_sub_unit_team"
        )
    ]

    def __str__(self):
        return self.name

    @admin.display(description="Number of Members")
    def get_number_of_members(self):
        return self.members.count()
