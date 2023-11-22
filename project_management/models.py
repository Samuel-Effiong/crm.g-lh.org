from typing import Tuple, Dict

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import numpy as np
import pandas as pd

from users.models import Shepherd


class Utility:
    pass


class DepartmentMemberManager(models.Manager):
    def get_department_members(self, department):
        """Get all the members that belongs to a specific department"""
        members = self.get_queryset().filter(department_name=department)
        return members

    def is_in_a_department(self, user):
        """Check if user is a member of any department"""
        member = self.get_queryset().filter(member_name=user)

        return len(member) > 0


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

    def get_member_image_url(self) -> str | None:
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
        return set(departments)

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
    department_name = models.CharField(_('Department (Short Name)'), max_length=255, unique=True)
    department_long_name = models.CharField(_('Department (Long Name)'), max_length=1000, null=True, blank=True)
    leader = models.ForeignKey(DepartmentMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    sub_leader = models.ForeignKey(DepartmentMember, on_delete=models.SET_NULL, blank=True, null=True, related_name='+')

    department_objectives = models.TextField()

    objects = DepartmentManager()

    class Meta:
        ordering = ('department_name', )

    def __str__(self):
        return f"{self.department_name}"

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

    def member_activity_in_a_department(self):
        members = self.member_names.all()
        member_completed_project = []

        for member in members:
            completed_project = DepartmentProject.objects.get_completed_projects(self, member)
            member_completed_project.append(len(completed_project))

        return members, member_completed_project


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
    project_name = models.CharField(max_length=1000)
    project_description = models.TextField()

    department_category = models.ForeignKey(DepartmentCategory, on_delete=models.CASCADE)
    project_members = models.ManyToManyField(DepartmentMember, blank=True)
    project_leader = models.ForeignKey(DepartmentMember, on_delete=models.CASCADE, null=True, blank=True, related_name='+')

    project_priority = models.CharField(max_length=50, default='Low', choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=50, blank=True, null=True, choices=STATUS_CHOICES)

    target = models.ManyToManyField(ProjectTarget, blank=True)

    start_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)

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



