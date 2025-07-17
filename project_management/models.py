import random
from typing import Tuple, Dict
from users.my_models import CustomUser

# from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model

from django.db import models
from django.db.models import Q, Sum, Count, Case, When, F, FloatField, Value
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# from users.models import Shepherd


class Utility:
    pass


WEIGHT_PROJECT_COMPLETED = 60
WEIGHT_PROJECT_OVERDUE = 50
WEIGHT_PROJECT_NOT_STARTED = 20

WEIGHT_TARGET_COMPLETED = 30
WEIGHT_TARGET_PENDING = 20
WEIGHT_TARGET_NOT_STARTED = 25


class DepartmentMemberManager(models.Manager):
    def get_department_members(self, department):
        """Get all the members that belongs to a specific department"""
        members = self.get_queryset().filter(department_name=department)
        return members

    def get_user_departments(self, user: CustomUser) -> list[str]:
        """Get a list of all the department a user is a member to"""
        departments_membership = self.get_queryset().filter(member_name=user)
        departments: list[str] = [department.department_name for department in departments_membership]

        return departments

    def is_in_a_department(self, user: CustomUser) -> bool:
        """Check if user is a member of any department"""
        member = self.get_queryset().filter(member_name=user)

        return len(self.get_user_departments(user)) > 0

    def get_top_and_lowest_performing_members(self, limit: int = None):
        """
        Retrieves a list of DepartmentMembers, sorted by their calculated performance score
        in descending order (highest score first).

        Args:
            limit (int, optional): The maximum number of top members to return.
                                   If None, returns all members. Defaults to None.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary contains:
                - 'member_id': The ID of the DepartmentMember.
                - 'member_name': The full name of the member's associated CustomUser.
                - 'performance_score': The calculated score for the member.
                - 'department_name': The name of the primary department this member belongs to.
                                     (Note: A member belongs to one Department in your model definition)
        """

        all_members = self.get_queryset().select_related('member_name', 'department_name')

        member_scores = []
        for member in all_members:
            score = member.get_performance_score()
            member_scores.append({
                'member_id': member.id,
                'member_name': member.member_name,
                'performance_score': score,
                'department_name': member.department_name.department_name if member.department_name else 'N/A'
            })

        # Sort the members by performance score in descending order
        member_scores.sort(key=lambda x: x['performance_score'], reverse=True)

        if limit:
            return {'top': member_scores[:limit], 'bottom': member_scores[-limit:][::-1]}
        return member_scores

    def get_ranking_of_performing_members_in_a_diaconate(self, limit, diaconate: 'Diaconate'):
        diaconate_members = self.get_queryset().filter(department_name__diaconate=diaconate)

        member_scores = []
        for member in diaconate_members:
            score = member.get_performance_score()
            member_scores.append({
                'member': member,
                'performance_score': score,
                'project_completed': member.departmentproject_set.filter(status='Completed').count(),
                'target_completed': member.departmentproject_set.filter(projecttarget__state='Completed').count(),
            })
        member_scores.sort(key=lambda x: x['performance_score'], reverse=True)
        if limit:
            return member_scores[:limit]


# Create your models here.
class DepartmentMember(models.Model):
    """A user that is a member of a department"""
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

    def get_performance_score(self) -> float:

        """
        Calculates the performance score for this specific DepartmentMember
        based on the projects they are involved in (as project_members) and
        the status of those projects and their associated targets.

        It rewards completed work and penalizes unstarted, in-progress,
        and especially overdue projects/targets this member is assigned to.

        Returns:
            float: The calculated performance score (0-100), rounded to 2 decimal places.
        """

        today = timezone.now().date()


        project_stats = DepartmentProject.objects.filter(
            project_members=self
        ).aggregate(
            total_member_projects=Count('pk', distinct=True),
            completed_member_projects=Count('pk', filter=Q(status='Completed'), distinct=True),
            active_member_projects=Count('pk', filter=Q(status='In Progress'), distinct=True),
            not_started_member_projects=Count('pk', filter=Q(status='Not Started'), distinct=True),
            overdue_member_projects=Count(
                'pk',
                filter=Q(due_date__lt=today, status__in=['In Progress', 'Not Started']),
                distinct=True
            ),

            total_member_targets=Count('target', distinct=True),
            completed_member_targets=Count('target', filter=Q(target__state='Completed'), distinct=True),
            pending_member_targets=Count('target', filter=Q(target__state='Pending Approval'), distinct=True),
            active_member_targets=Count('target', filter=Q(target__state='In Progress'), distinct=True),
            not_started_member_targets=Count('target', filter=Q(target__state='Not Started'), distinct=True)
        )

        total_projects = project_stats.get('total_member_projects') or 0
        completed_projects = project_stats.get('completed_member_projects') or 0
        active_projects = project_stats.get('active_member_projects') or 0
        not_started_projects = project_stats.get('not_started_member_projects') or 0
        overdue_projects = project_stats.get('overdue_member_projects') or 0

        total_targets = project_stats.get('total_member_targets') or 0
        completed_targets = project_stats.get('completed_member_targets') or 0
        pending_targets = project_stats.get('pending_member_targets') or 0
        active_targets = project_stats.get('active_member_targets') or 0
        not_started_targets = project_stats.get('not_started_member_targets') or 0

        score = 0.0  # Initialize the member's performance score

        # Calculate project-based contributions to the score

        if total_projects > 0:
            score += (completed_projects / total_projects) * WEIGHT_PROJECT_COMPLETED
            score -= (overdue_projects / total_projects) * WEIGHT_PROJECT_OVERDUE
            score -= (not_started_projects / total_projects) * WEIGHT_PROJECT_NOT_STARTED

            # Calculate target-based contributions to the score
        if total_targets > 0:
            score += (completed_targets / total_targets) * WEIGHT_TARGET_COMPLETED
            score -= (pending_targets / total_targets) * WEIGHT_TARGET_PENDING
            score -= (not_started_targets / total_targets) * WEIGHT_TARGET_NOT_STARTED

        # Clamp the score to a reasonable range, e.g., 0 to 100
        score = max(0.0, min(100.0, score))

        return round(score, 2)


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

    # def get_performance_score_for_diaconate_departments

    def get_overview_statistics_for_diaconate_departments(self, diaconate_instance: 'Diaconate') -> models.QuerySet:
        """Get all the overview statistics in a particular diaconate"""
        today = timezone.now().date()

        statistics = Department.objects.filter(department_diaconate=diaconate_instance).annotate(
            num_members=Count('member_names', distinct=True),
            # --- Project - related counts  ---
            total_projects=Count('departmentproject', distinct=True),
            num_completed_projects=Count('departmentproject', filter=Q(departmentproject__status='Completed'), distinct=True),
            num_active_projects=Count('departmentproject', filter=Q(departmentproject__status='In Progress'), distinct=True),
            num_not_started_projects=Count('departmentproject', filter=Q(departmentproject__status='Not Started'), distinct=True),
            num_overdue_projects=Count(
                'departmentproject',
                filter=Q(
                    departmentproject__due_date__lt=today,
                    departmentproject__status__in=['In Progress', 'Not Started']
                ), distinct=True
            ),

            # --- Target-related counts ---
            total_targets=Count('departmentproject__target', distinct=True),
            num_completed_targets=Count(
                'departmentproject__target',
                filter=Q(departmentproject__target__state='Completed'),
                distinct=True
            ),
            num_pending_approval_targets=Count(
                'departmentproject__target',
                filter=Q(departmentproject__target__state='Pending Approval'),
                distinct=True
            ),
            num_active_targets=Count(
                'departmentproject__target',
                filter=Q(departmentproject__target__state='In Progress'),
                distinct=True
            ),
            num_not_started_targets=Count(
                'departmentproject__target',
                filter=Q(departmentproject__target__state='Not Started'),
                distinct=True
            ),

            resource_allocation_index_projects=Case(
                When(num_members__gt=0, then=F('num_active_projects') * 1.0 / F('num_members')),
                default=Value(0.0),
                output_field=FloatField()
            ),
            # --- NEW: Resource Allocation Index (Targets per Member) ---
            resource_allocation_index_targets=Case(
                When(num_members__gt=0, then=F('num_active_targets') * 1.0 / F('num_members')),
                default=Value(0.0),
                output_field=FloatField()
            ),
        )
        return statistics


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

    department_objectives = models.TextField(null=True, blank=True, default="")
    custom_tables = models.ManyToManyField('DepartmentTable', blank=True)

    department_diaconate = models.ForeignKey('Diaconate', on_delete=models.CASCADE)
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
        return self.member_names.count()

    @admin.display(description='No of Category')
    def get_no_of_categories(self) -> int:
        return self.department_categories.count()

    def get_no_of_units(self) -> int:
        """Get the number of units in this department"""
        return self.unit_set.count() if hasattr(self, 'unit_set') else 0

    def get_no_of_targets(self):
        targets = ProjectTarget.objects.filter(project__department=self)
        return targets.count()

    def get_no_of_subunits(self) -> int:
        """Get the number of subunits in this department"""
        return SubUnit.objects.filter(unit_name__unit_department__department_name=self.department_name).count()

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

    def get_overview_statistic(self):
        """Calculates comprehensive overview statistics for this specific Department instance,
        including counts of member etc
        """

        today = timezone.now().date()

        statistics = DepartmentProject.objects.filter(
            department=self
        ).aggregate(
            total_projects=Count('pk', distinct=True),
            completed_projects=Count('pk', filter=Q(status='Completed'), distinct=True),
            active_projects=Count('pk', filter=Q(status='In Progress'), distinct=True),
            not_started_projects=Count('pk', filter=Q(status='Not Status'), distinct=True),
            overdue_projects=Count(
                'pk',
                filter=Q(due_date__lt=today, status__in=['In Progress', 'Not Started']), distinct=True),

            total_targets=Count('target', distinct=True),
            completed_targets=Count('target', filter=Q(target__state='Pending Approval'), distinct=True),
            pending_targets=Count('target', filter=Q(target__state='In Progress'), distinct=True),
            active_targets=Count('target', filter=Q(target__state='Completed'), distinct=True),
            not_started_targets_in_targets=Count('target', filter=Q(target__state='Not Started'), distinct=True),
        )

        return statistics

    def calculate_performance_score(self):
        """
        Calculates a custom 'performance score' for this specific department based on aggregated
        project and target statistics.
        """
        statistics = self.get_overview_statistic()

        total_projects = statistics.get('total_projects') or 0
        completed_projects = statistics.get('completed_projects') or 0
        active_projects = statistics.get('active_projects') or 0
        not_started_projects = statistics.get('not_started_projects') or 0
        overdue_projects = statistics.get('overdue_projects') or 0

        total_targets = statistics.get('total_targets') or 0
        completed_targets = statistics.get('completed_targets') or 0
        pending_targets = statistics.get('pending_targets') or 0
        active_targets = statistics.get('active_targets') or 0
        not_started_targets = statistics.get('not_started_targets_in_targets') or 0

        score = 0.0

        if total_projects > 0:
            score += (completed_projects / total_projects) * WEIGHT_PROJECT_COMPLETED
            score -= (overdue_projects / total_projects) * WEIGHT_PROJECT_OVERDUE
            score -= (not_started_projects / total_projects) * WEIGHT_PROJECT_NOT_STARTED

        if total_targets > 0:
            score += (completed_targets / total_targets) * WEIGHT_TARGET_COMPLETED
            score -= (pending_targets / total_targets) * WEIGHT_TARGET_PENDING
            score -= (not_started_targets / total_targets) * WEIGHT_TARGET_NOT_STARTED

        score = max(0.0, min(100.0, score))

        return score


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
    target_description = models.TextField(default="")
    project = models.ForeignKey('DepartmentProject', on_delete=models.CASCADE)
    state = models.CharField(max_length=25, choices=Choices, default='Not Started')
    date = models.DateField(auto_now=True)
    due_date = models.DateField()

    objects = ProjectTargetManager()

    def __str__(self):
        return self.target_name

    class Meta:
        verbose_name_plural = 'Project Targets'
        ordering = ('-date', )

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

    def get_overdue_projects(self):
        """
        Retrieves all project that are past their due date and are not yet completed,
        regardless of department or other organizational structure
        """
        return self.get_queryset().filter(
            due_date__lt=timezone.now().date(),
            status__in=['In Progress', 'Not Started']
        )


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
    status = models.CharField(max_length=50, default="Not Started", choices=STATUS_CHOICES)

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
        completed_target = targets.filter(state='Completed')
        try:
            complete_percentage = int((len(completed_target) / targets.count()) * 100)
        except ZeroDivisionError:
            complete_percentage = 0

        return complete_percentage

    def get_completed_targets(self):
        return self.target.filter(state='Completed')


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
        group_id = self.department_category.category_name if self.department_category else ""
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
        return reverse_lazy('project_management:project-detail', args=[self.department.department_name, self.id])


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
    FIELD_TYPE_CHOICES = (
        ('text', 'text'),
        ('password', 'password'),
        ('textarea', 'textarea'),
        ('email', 'email'),
        ('number', 'number'),
        ('checkbox', 'checkbox'),
        ('tel', 'tel'),
        ('url', 'url'),
        ('date', 'date'),
        ('time', 'time'),
        ('file', 'file'),
        ('search', 'search'),
        ('range', 'range'),
        ('color', 'color'),
        ('month', 'month'),
        ('week', 'week'),
        ('datetime-local', 'datetime-local'),
    )
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=255, choices=FIELD_TYPE_CHOICES)
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
    def get_overview_statistics(self):
        today = timezone.now().date()

        statistics = Diaconate.objects.annotate(
            num_members=Count('departments__member_names', distinct=True),

            # --- Project - related counts  ---
            total_projects=Count('departments__departmentproject', distinct=True),
            num_completed_projects=Count(
                'departments__departmentproject',
                filter=Q(departments__departmentproject__status='Completed'),
                distinct=True
            ),
            num_active_projects=Count(
                'departments__departmentproject',
                filter=Q(departments__departmentproject__status='In Progress'),
                distinct=True
            ),
            num_not_started_projects=Count(  # Projects with 'Not Started' status
                'departments__departmentproject',
                filter=Q(departments__departmentproject__status='Not Started'),
                distinct=True
            ),
            num_overdue_projects=Count(
                'departments__departmentproject',
                filter=Q(
                    departments__departmentproject__due_date__lt=today,
                    departments__departmentproject__status__in=['In Progress', 'Not Started'],
                ),
                distinct=True
            ),

            # --- Target-related counts ---
            total_targets=Count('departments__departmentproject__target', distinct=True),
            num_completed_targets=Count(
                'departments__departmentproject__target',
                filter=Q(departments__departmentproject__target__state='Completed'),
                distinct=True
            ),
            num_pending_targets=Count(
                'departments__departmentproject__target',
                filter=Q(departments__departmentproject__target__state='Pending Approval'),
                distinct=True
            ),
            num_active_targets=Count(
                'departments__departmentproject__target',
                filter=Q(departments__departmentproject__target__state='In Progress'),
                distinct=True
            ),
            num_not_started_targets=Count(
                'departments__departmentproject__target',
                filter=Q(departments__departmentproject__target__state='Not Started'),
                distinct=True
            ),
        )

        return statistics.order_by('name')

    def get_performance_score_for_each_diaconate(self):

        results = []

        diaconate_stats_queryset = self.get_overview_statistics()

        diaconate_name = []
        diaconate_perf_score = []

        for diaconate in diaconate_stats_queryset:
            score = 0.0  # Initial score

            if diaconate.total_projects > 0:
                score += (diaconate.num_completed_projects / diaconate.total_projects) * WEIGHT_PROJECT_COMPLETED
                # Negative contributions from overdue and not started projects
                score -= (diaconate.num_overdue_projects / diaconate.total_projects) * WEIGHT_PROJECT_OVERDUE
                score -= (diaconate.num_not_started_projects / diaconate.total_projects) * WEIGHT_PROJECT_NOT_STARTED

            if diaconate.total_targets > 0:
                score += (diaconate.num_completed_targets / diaconate.total_targets) * WEIGHT_TARGET_COMPLETED
                # Negative contributions from pending and not started targets
                score -= (diaconate.num_pending_targets / diaconate.total_targets) * WEIGHT_TARGET_PENDING
                score -= (diaconate.num_not_started_targets / diaconate.total_targets) * WEIGHT_TARGET_NOT_STARTED

            score = max(0.0, min(100.0, score))

            diaconate_name.append(diaconate.name)
            diaconate_perf_score.append(round(score, 2))

        results = {
            'diaconate_names': diaconate_name,
            'diaconate_perf_score': diaconate_perf_score
        }

        return results

    def get_overall_performance_score(self):
        today = timezone.now().date()

        # Define weights for the performance score components (adjust as needed)
        # These should be consistent with how you score individual Diaconates if comparing.

        # Step 1: Aggregate all necessary project counts for the entire organization
        project_counts = DepartmentProject.objects.aggregate(
            total_projects=Count('pk', distinct=True),
            completed_projects=Count('pk', filter=Q(status='Completed'), distinct=True),
            active_projects=Count('pk', filter=Q(status='In Progress'), distinct=True),
            not_started_projects=Count('pk', filter=Q(status='Not Started'), distinct=True),
            overdue_projects=Count(
                'pk',
                filter=Q(due_date__lt=today, status__in=['In Progress', 'Not Started']),
                distinct=True
            )
        )

        # Step 2: Aggregate all necessary target counts for the entire organization
        target_counts = ProjectTarget.objects.aggregate(
            total_targets=Count('pk', distinct=True),
            completed_targets=Count('pk', filter=Q(state='Completed'), distinct=True),
            pending_targets=Count('pk', filter=Q(state='Pending Approval'), distinct=True),
            active_targets=Count('pk', filter=Q(state='In Progress'), distinct=True),
            not_started_targets=Count('pk', filter=Q(state='Not Started'), distinct=True)
        )

        # Step 3: Initialize and calculate the overall score
        overall_score = 0.0

        # Project-based contribution
        total_projects = project_counts.get('total_projects', 0)
        if total_projects > 0:
            overall_score += (project_counts.get('completed_projects', 0) / total_projects) * WEIGHT_PROJECT_COMPLETED
            overall_score -= (project_counts.get('overdue_projects', 0) / total_projects) * WEIGHT_PROJECT_OVERDUE
            overall_score -= (project_counts.get('not_started_projects', 0) / total_projects) * WEIGHT_PROJECT_NOT_STARTED

        # Target-based contribution
        total_targets = target_counts.get('total_targets', 0)
        if total_targets > 0:
            overall_score += (target_counts.get('completed_targets', 0) / total_targets) * WEIGHT_TARGET_COMPLETED
            overall_score -= (target_counts.get('pending_targets', 0) / total_targets) * WEIGHT_TARGET_PENDING
            overall_score -= (target_counts.get('not_started_targets', 0) / total_targets) * WEIGHT_TARGET_NOT_STARTED

        # Clamp the score to a reasonable range, e.g., 0 to 100
        overall_score = max(0.0, min(100.0, overall_score))

        # Step 4: Combine all results into a single dictionary
        results = {
            'performance_score': round(overall_score, 2),
        }

        return results


class Diaconate(models.Model):
    name = models.CharField(max_length=500, unique=True)
    info = models.TextField(null=True, blank=True)
    head = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    assistant = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    departments = models.ManyToManyField(Department, blank=True, null=True)
    objects = CustomDiaconateManager()

    def __str__(self):
        return f"{self.name}"

    @admin.display(description="Number of Departments")
    def get_number_of_departments(self) -> int:
        return self.departments.count()

    def get_number_of_members_in_diaconate(self):
        return DepartmentMember.objects.filter(department_name__department_diaconate=self).count()

    # FIXME: Create a function to get the overall statistics once
    def get_number_of_projects_in_diaconate(self):
        return DepartmentProject.objects.filter(department__department_diaconate=self).count()

    def is_a_diaconate_member(self, user):

        # check if this user belongs to any department that is part of 
        # this diaconate
        
        result = self.departments.filter(member_names__member_name=user)
        return result

    def is_admin_staff(self, user):
        """Display the diaconate link on the user home dashboard if the user is a staff in any
        of the department under the diaconate
        """

        if self.head and self.assistant:
            
            if user.username == self.head.username or user.username == self.assistant.username:
                return True
            elif user.level == 'chief_shep':
                return True
            elif user.is_superuser:
                return True
            
        return False
    
    def get_absolute_url(self) -> str:
        return reverse_lazy("diaconate:treasury-dashboard")

    def calculate_performance_score(self):
        """
        Calculate the performance score for the Diaconate based on the projects and targets
        across all departments under this diaconate.
        """

        stats = DepartmentProject.objects.filter(
            department__in=self.departments.all()
        ).aggregate(
            total_projects=Count('pk', distinct=True),
            completed_projects=Count('pk', filter=Q(status='Completed'), distinct=True),
            active_projects=Count('pk', filter=Q(status='In Progress'), distinct=True),
            not_started_projects=Count('pk', filter=Q(status='Not Started'), distinct=True),
            overdue_projects=Count(
                'pk',
                filter=Q(due_date__lt=timezone.now().date(), status__in=['In Progress', 'Not Started']),
                distinct=True
            ),

            total_targets=Count('target', distinct=True),
            completed_targets=Count('target', filter=Q(target__state='Completed'), distinct=True),
            pending_targets=Count('target', filter=Q(target__state='Pending Approval'), distinct=True),
            not_started_targets=Count('target', filter=Q(target__state='Not Started'), distinct=True),
        )

        # Extract aggregated values, providing defaults of 0
        total_projects = stats.get('total_projects') or 0
        completed_projects = stats.get('completed_projects') or 0
        active_projects = stats.get('active_projects') or 0
        not_started_projects = stats.get('not_started_projects') or 0
        overdue_projects = stats.get('overdue_projects') or 0

        total_targets = stats.get('total_targets') or 0
        completed_targets = stats.get('completed_targets') or 0
        pending_targets = stats.get('pending_targets') or 0
        active_targets = stats.get('active_targets') or 0
        not_started_targets = stats.get('not_started_targets_in_targets') or 0

        score = 0.0

        # Calculate project-based contributions to the score
        if total_projects > 0:
            score += (completed_projects / total_projects) * WEIGHT_PROJECT_COMPLETED
            score -= (overdue_projects / total_projects) * WEIGHT_PROJECT_OVERDUE
            score -= (not_started_projects / total_projects) * WEIGHT_PROJECT_NOT_STARTED

        # Calculate target-based contributions to the score
        if total_targets > 0:
            score += (completed_targets / total_targets) * WEIGHT_TARGET_COMPLETED
            score -= (pending_targets / total_targets) * WEIGHT_TARGET_PENDING
            score -= (not_started_targets / total_targets) * WEIGHT_TARGET_NOT_STARTED

        score = max(0.0, min(100.0, score))

        return {
            'performance_score': round(score, 2),
            # Include all raw counts for transparency
            'total_projects': total_projects,
            'completed_projects': completed_projects,
            'active_projects': active_projects,
            'not_started_projects': not_started_projects,
            'overdue_projects': overdue_projects,
            'total_targets': total_targets,
            'completed_targets': completed_targets,
            'pending_targets': pending_targets,
            'active_targets': active_targets,
            'not_started_targets_in_targets': not_started_targets,
        }


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
