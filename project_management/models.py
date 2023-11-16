from typing import Tuple, Dict

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model

from django.db import models
from django.urls import reverse
from django.utils import timezone

import numpy as np
import pandas as pd

from users.models import Shepherd


class Utility:
    pass


class DepartmentMemberManager(models.Manager):
    def get_department_members(self, department):
        """Get all the members that belogns to a specific department"""
        members = self.get_queryset().filter(department_name=department)
        return members


# Create your models here.
class DepartmentMember(models.Model):
    """A user that is a member of a department

    FIXME: There is an implied bug that allows a users to be added twice to the
    FIXME: same Department

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

    def department_leaders(self):
        leaders = [department.leader.name for department in self.get_queryset()]
        return leaders


class Department(models.Model):
    CHOICES = (
        ('GMT', 'GMT'),
        ('Extraction', 'Extraction Team'),
        ('Website', 'Website Team'),
        ('Archive', 'Archive'),
    )

    member_names = models.ManyToManyField(DepartmentMember, blank=True)
    department_categories = models.ManyToManyField(DepartmentCategory, blank=True)
    department_name = models.CharField(max_length=255, unique=True, choices=CHOICES)
    leader = models.ForeignKey(Shepherd, on_delete=models.CASCADE)
    sub_leader = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True, related_name='+')

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

    def department_leaders(self):
        leaders = Department.objects.department_leaders()
        return leaders

    def is_leader(self, user) -> bool:
        return self.leader.name == user


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
    is_approved = models.BooleanField(default=True)

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

    project_priority = models.CharField(max_length=50, blank=True, null=True, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=50, blank=True, null=True, choices=STATUS_CHOICES)

    target = models.ManyToManyField(ProjectTarget, blank=True)

    start_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)

    objects = DepartmentProjectManager()

    def __str__(self):
        return self.project_name

    class Meta:
        verbose_name_plural = 'Department Projects'
        ordering = ('due_date', )

    @admin.display(description="No of Workers")
    def get_no_of_workers(self):
        project_members = self.project_members.all()

        return len(project_members)

    @admin.display(description='No of Targets')
    def get_no_of_target(self):
        target = self.target.all()
        return len(target)

    def get_complete_percentage(self):
        targets = self.target.all()

        # get targets that are completed
        completed_target = [target for target in targets if target.state == 'Completed' and target.is_approved]
        try:
            complete_percentage = (len(completed_target) / len(targets)) * 100
        except ZeroDivisionError:
            complete_percentage = 0

        return complete_percentage



