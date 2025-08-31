import json
from typing import Any, Dict
from datetime import datetime

import pandas as pd
from django.core.signals import request_started
from django.db.models import Count, Q

from django_htmx.http import HttpResponseClientRedirect

from django.db import models, transaction, IntegrityError

from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.utils import timezone
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.http import (HttpResponseRedirect, JsonResponse,
                         HttpResponseForbidden, HttpResponse)

import diaconate
from users.my_models import CustomUser
from .models import (
    Department, DepartmentMember, DepartmentCategory,
    DepartmentProject, ProjectTarget, DepartmentTable,
    CustomField, FieldValue, FieldValueIndex,

    Diaconate, Unit, SubUnit, Team
)
from users.models import Shepherd, SubShepherd

from home.models import Notification
from users.my_models.utilities import convert_to_format

from diaconate.models import TreasuryRequest

from .services import super_user_details, handle_view_details_for_various_roles

title = 'GLH-FAM'
project_title = 'GLH-PROJ'
required_groups = ['Diakonate Head', 'Department Head']


def is_member(user):
    """A utitlity function to check is a user belongs to any department"""
    member = DepartmentMember.objects.filter(member_name=user)
    return len(member) > 0


class PartialsView:
    def get_departments(self, request, all_department_option=None, department_filter=None):
        diaconate_name = request.GET.get('diaconate_selection')
        departments = Department.objects.none()

        user = request.user

        user_leader_in_dept = Department.objects.filter(
            Q(leader__member_name=user) | Q(sub_leader__member_name=user)
        )

        if diaconate_name:
            try:
                diaconate = Diaconate.objects.get(name=diaconate_name)
                departments = diaconate.departments.all()
            except Diaconate.DoesNotExist:
                pass

            if all_department_option is not None:
                all_department_option = all_department_option.strip()

        context = {
            'departments': departments,
           'all_department_option': True if all_department_option else False,
        }

        if department_filter is not None:
            context['user_leader_in_dept'] = user_leader_in_dept

        return render(request, 'project_management/partial_html/dashboard/get_departments_options.html', context=context)

    def get_project_targets_by_filter(self, request, project_id):
        department_project = DepartmentProject.objects.get(id=project_id)
        department = department_project.department

        filter = request.GET.get('filter', None)

        filtered_project_targets = department_project.target.filter(status=filter)

    def change_target_status(self, request, target_id=None):

        if target_id:
            project_target = ProjectTarget.objects.get(id=target_id)
            department_project = project_target.project

        try:
            with transaction.atomic():
                leader_approval = request.GET.get('leader_approval', None)
                delete_target = request.GET.get('delete_target', None)

                if leader_approval:
                    project_target.state = leader_approval

                    if leader_approval == 'Completed':
                        project_target.date = timezone.now()

                    project_target.save()
                    department_project.update_current_status_of_project_target()

                elif delete_target:
                    project_target.delete()
                    project_target.save()

                    department_project.update_current_status_of_project_target()

                else:

                    update_state = request.GET.get('update_target_state')

                    project_target.state = update_state
                    project_target.save()

                    department_project.update_current_status_of_project_target()
        except Exception as e:
            pass

        context = {
            'object': department_project,
        }

        return render(
            request,
            'project_management/partial_html/project_detail/update_project_status.html',
            context=context
        )

    def get_members(self, request):
        department = request.GET.get('department_selection', None)

        context = {}

        if department:
            department = Department.objects.get(id=department)
            context['department'] = department
            
        return render(request, 'project_management/partial_html/project_members/get_members.html', context=context)


class ProjectManagementView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/index.html'

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=required_groups).exists() or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponse("You are not authorized to be here...please turn back")

    def get(self, request, *args, **kwargs):

        department_dashboard = kwargs.get('department', None)
        if department_dashboard:

            if 'delete_table_id' in request.GET:
                delete_table_id = request.GET['delete_table_id']

                department = Department.objects.get(department_name=department_dashboard)

                department_table = department.custom_tables.get(id=delete_table_id)
                department_table.delete()

                return JsonResponse({})

            return super().get(request, *args, **kwargs)
        else:
            # check if any department has been created
            # if the user is a superuser redirect to the admin setting
            # page else direct a normal user to contact the admin

            # Get the department the user is in and select the first
            if request.user.is_superuser:
                pass
                member_department = Department.objects.count()

                if member_department == 0:
                    return HttpResponseRedirect(reverse_lazy('project_management:project-admin-settings'))
            else:
                # A Diakonate can explicitly not be in any department to have access to the site

                member_department = Department.objects.get_member_departments(request.user)

                if not member_department and not request.user.groups.filter(name__in=required_groups).exists():
                    return HttpResponseForbidden("Please Join A Department before you can access this page.")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        user = self.request.user

        # context['category'] = kwargs.get('department', "")

        context['page'] = 'Dashboard'

        context['title'] = title
        context['user'] = user
        context['project_title'] = project_title
        # context['department_name'] = f"{kwargs.get('department', "")} Dashboard"

        # department = Department.objects.get(department_name=context['category'])
        # context['department'] = department

        # Context needed to handle the navigation
        # Handle the view for super admin

        handle_view_details_for_various_roles(context)

        # if user.is_superuser:  # Overview stats of all the organization
        #     # Exclusively for the super admin
        #     super_user_details(context, )
        #
        # else:
        #     # For a normal user, get the department they belong to
        #     context['member_departments'] = Department.objects.get_member_departments(user)

        # For Both Super User and Normal User
        # only ensure that the appropriate roles only see what is relevant to them
        context['department_leaders'] = [leader.member_name for leader in Department.objects.department_leaders() if leader]

        # try:
        #     department_member = DepartmentMember.objects.get(member_name=user, department_name=department)
        #     context['department_membership'] = department_member
        #     # context['is_department_leader'] = department.is_leader(department_member)
        # except DepartmentMember.DoesNotExist:
        #     context['is_department_leader'] = False

        # department_projects = DepartmentProject.objects.filter(department=department, status__in=['In Progress', 'Not Started'])
        # context['department_projects'] = department_projects
        #
        # department_projects_status_statistic = DepartmentProject.objects.get_department_projects_status_statistic(department)
        # context['department_project_status_statistic'] = department_projects_status_statistic

        # all_department_pending_target = ProjectTarget.objects.all_department_pending_target(department)
        # context['all_department_pending_target'] = all_department_pending_target

        # GET Member Activity in the project
        # members, complete_project = department.member_activity_in_a_department()
        # context['member_activity_in_a_department'] = zip(members, complete_project)

        # context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

        # check if there is a treasury diaconate and adds a special link section
        # to access treasury related pages
        try:
            treasury = Diaconate.objects.get(name='TREASURY')
            membership = treasury.is_a_diaconate_member(user)

            if membership:
                context['treasury_membership'] = True
        except Diaconate.DoesNotExist as e:
            context['treasury_diaconate_unavailable'] = True

        # activate the special diaconate features

        # check if the user belongs to a treasury diaconate

        return context

    def post(self, request, *args, **kwargs):

        dashboard_selection = request.POST.get('dashboard_selection', None)
        if dashboard_selection:
            diaconate_selection = request.POST.get('diaconate_selection', None)  # contains the actual diaconate selection
            department_selection = request.POST.get('department_selection', None)  # contains the actual department selection
            submit_button = request.POST['submit_button']

            context = self.get_context_data(**kwargs)

            diaconate = Diaconate.objects.get(name=diaconate_selection)
            context['diaconate'] = diaconate

            if diaconate_selection:
                # To check to ensure that the diaconate selection is not empty
                # This is to indicate that the dynamic switching between levels was selected

                if submit_button == 'diakonate':
                    # Accessible only by diakonate head and super admin
                    no_of_members_in_diaconate = DepartmentMember.objects.filter(
                        department_name__department_diaconate__name=diaconate_selection
                    ).count()

                    context['no_of_members_in_diaconate'] = no_of_members_in_diaconate

                    diaconate_stats = diaconate.calculate_performance_score()

                    context['diaconate_performance_score'] = diaconate_stats['performance_score']
                    context['no_of_active_project_in_diaconate'] = diaconate_stats['active_projects']
                    context['no_of_completed_project_in_diaconate'] = diaconate_stats['completed_projects']
                    context['no_of_not_started_project_in_diaconate'] = diaconate_stats['not_started_projects']
                    context['total_projects_in_diaconate'] = diaconate_stats['total_projects']

                    department_chart_data = Department.objects.get_overview_statistics_for_diaconate_departments(diaconate)

                    department_categories = [data.department_name for data in department_chart_data]
                    department_members = [data.num_members for data in department_chart_data]

                    # Project Related data
                    department_total_projects = [data.total_projects for data in department_chart_data]
                    department_active_projects = [data.num_active_projects for data in department_chart_data]
                    department_not_started_projects = [data.num_not_started_targets for data in department_chart_data]
                    department_completed_projects = [data.num_completed_projects for data in department_chart_data]
                    department_overdue_projects = [data.num_overdue_projects for data in department_chart_data]

                    # Target Related data
                    department_total_targets = [data.total_targets for data in department_chart_data]
                    department_active_targets = [data.num_active_targets for data in department_chart_data]
                    department_not_started_targets = [data.num_not_started_targets for data in department_chart_data]
                    department_completed_targets = [data.num_completed_targets for data in department_chart_data]
                    department_pending_approval_targets = [data.num_completed_targets for data in department_chart_data]
                    # department_overdue_targets = [data.num_overdue_targets for data in department_chart_data]

                    department_resource_allocation_index_projects = [data.resource_allocation_index_projects for data in department_chart_data]
                    department_resource_allocation_index_targets = [data.resource_allocation_index_targets for data in department_chart_data]

                    department_performance_scores = [data.calculate_performance_score() for data in department_chart_data]

                    context['department_chart_data'] = {
                        'categories': json.dumps(department_categories),
                        'members': json.dumps(department_members),

                        'total_projects': json.dumps(department_total_projects),
                        'active_projects': json.dumps(department_active_projects),
                        'not_started_projects': json.dumps(department_not_started_projects),
                        'completed_projects': json.dumps(department_completed_projects),
                        'overdue_projects': json.dumps(department_overdue_projects),

                        'total_targets': json.dumps(department_total_targets),
                        'active_targets': json.dumps(department_active_targets),
                        'not_started_targets': json.dumps(department_not_started_targets),
                        'completed_targets': json.dumps(department_completed_targets),
                        'pending_approval_targets': json.dumps(department_pending_approval_targets),
                        'department_resource_allocation_index_projects': json.dumps(department_resource_allocation_index_projects),
                        'department_resource_allocation_index_targets': json.dumps(department_resource_allocation_index_targets),
                        # 'overdue_targets': json.dumps(department_overdue_targets),

                        'department_performance_score': json.dumps(department_performance_scores),
                    }

                    # Get the top performing worker in a particular diaconate
                    diaconate_workers_performing_score = DepartmentMember.objects.get_ranking_of_performing_members_in_a_diaconate(10, diaconate)
                    context['diaconate_workers_performing_score'] = diaconate_workers_performing_score

                elif submit_button == 'department':
                    # Accessible by department leader, diakonate head and super admin
                    department = diaconate.departments.get(department_name=department_selection)
                    context['department'] = department

                    department_stats = department.get_overview_statistic()
                    context['department_stats'] = department_stats

                    # context['']

            context['display_category'] = submit_button
            return render(request, 'project_management/partial_html/dashboard/diakonate_dashboard.html', context=context)

        department = kwargs['department']
        department = Department.objects.get(department_name=department)

        table_name = request.POST['table_name'].title().split()
        table_name = "".join(table_name)

        table_name_plural = request.POST['table_name_plural']
        table_description = request.POST['table_description']

        # Define the DepartmentTable
        department_table = DepartmentTable.objects.create(
            table_name=table_name,
            table_name_plural=table_name_plural,
            table_description=table_description,
            department_name=department
        )

        field_id = request.POST['field_id']
        field_id = list(set(field_id.split()))

        fields = []

        foreign_keys = ['department_member', 'family_member']

        for id in field_id:
            field_name = f"field_name_{id}"
            if field_name in request.POST:
                field_type = request.POST[f'field_type_{id}']
                field_name = request.POST[field_name]

                field = CustomField.objects.create(
                    name=field_name, 
                    field_type=field_type,
                    table=department_table
                )
                fields.append(field)
        
        # Add fields to the department table
        department_table.fields.add(*fields)

        # add department table to the department
        department.custom_tables.add(department_table)

        return HttpResponseRedirect(reverse_lazy('project_management:department_dashboard', args=[kwargs['department']]))


class DepartmentProjectListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/project-index.html'

    def test_func(self):
        user = self.request.user

        return user.groups.filter(name__in=required_groups).exists() or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponse("You are not authorized to be here...please turn back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        # category = kwargs['department']

        context['page'] = 'Project'
        # context['category'] = category

        context['title'] = title
        context['project_title'] = project_title
        context['user'] = user

        # department = Department.objects.get(department_name=category)

        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

        user_leader_in_dept = Department.objects.filter(
            Q(leader__member_name=user) | Q(sub_leader__member_name=user)
        )
        context['user_leader_in_dept'] = user_leader_in_dept

        if user.is_superuser:

            user_diaconates = Diaconate.objects.all()
            context['diaconates'] = user_diaconates

            context['department_projects'] = DepartmentProject.objects.order_by('-due_date')

            context['member_departments'] = Department.objects.all()
        elif user.groups.filter(name="Diakonate Head"):  # If user is a diakonate head
            # Get all the diaconate that belongs to this user is a leader/ assistant in
            user_diaconates = Diaconate.objects.filter(Q(head=user) | Q(assistant=user))
            context['diaconates'] = user_diaconates

            # Get all the department that this diaconate is under these diaconates
            department_queryset = Department.objects.filter(department_diaconate__in=user_diaconates)
            context['member_departments'] = department_queryset  # Use to display the drop down list of the department in the sidenav

            department_project_queryset = DepartmentProject.objects.filter(department__department_diaconate__in=user_diaconates)
            context['department_projects'] = department_project_queryset.exclude(status='Completed').order_by('-due_date')

        elif user.groups.filter(name='Department Head'):  # If user is a departmental head
            # Get all the departments that this user is a leader/ sub leader in
            user_departments = Department.objects.filter(Q(leader__member_name=user) | Q(sub_leader__member_name=user))

            # Get all the diaconate that this user is in
            user_diaconates = Diaconate.objects.filter(department__in=user_departments).distinct()
            context['diaconates'] = user_diaconates

            context['member_departments'] = user_departments

            department_project_queryset = DepartmentProject.objects.filter(department__in=user_departments)
            context['department_projects'] = department_project_queryset.exclude(status='Completed').order_by('-due_date')

        # department_projects = DepartmentProject.objects.filter(department=department)
        if 'filter' in self.request.GET:
            status = self.request.GET['status']
            priority = self.request.GET['priority']

            if status != 'All':
                department_projects = context['department_projects'].filter(status=status)
            if priority != 'All':
                department_projects = context['department_projects'].filter(project_priority=priority)

            context['filter_by_status'] = status
            context['filter_by_priority'] = priority
        else:
            context['filter_by_status'] = 'All'
            context['filter_by_priority'] = 'All'

        # context['department_projects'] = department_projects

        # context['department_categories'] = DepartmentCategory.objects.get_department_categories(department)
        # context['department_members'] = DepartmentMember.objects.get_department_members(department)

        # try:
        #     context['is_department_leader'] = department.is_leader(department_member)
        # except UnboundLocalError:
        #     # Must be a superuser to activate this error
        #     context['is_department_leader'] = False

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # Check if the post-request is for filtering the project
        if 'project_filter' in request.POST:
            priority = request.POST.get('priority', 'All')
            status = request.POST.get('status', 'All')
            diaconate = request.POST.get('diakonate', "all")
            department = request.POST.get('department', "all")

            projects = DepartmentProject.objects.all()

            # Filter first by diaconate
            if diaconate != 'all':
                projects = projects.filter(department__department_diaconate__name=diaconate)
            else:
                # pass every project that this user is part of the diaconate
                projects.filter(department__department_diaconate__in=context['diaconates'])

            if department != "all":
                projects = projects.filter(department__department_name=department)

            if status != 'All':
                projects = projects.filter(status=status)

            if priority != 'All':
                projects = projects.filter(project_priority=priority)

            context['department_projects'] = projects

            return render(request, 'project_management/partial_html/project_list/filtered_projects.html', context=context )

        try:
            department_id = request.POST.get('dept', None)
            project_name = request.POST.get('project_name', None)
            project_description = request.POST.get('project_description', None)
            due_date = request.POST.get('due_date', None)

            department = Department.objects.get(id=department_id)
            department_project = DepartmentProject.objects.create(
                department=department,
                project_name=project_name,
                project_description=project_description,
                due_date=due_date
            )
        except Exception as e:
            context = self.get_context_data(**kwargs)
            context['error'] = str(e)
            return self.render_to_response(context=context)

        return HttpResponseRedirect(reverse_lazy('project_management:project'))


class DepartmentProjectDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/project-detail.html'
    model = DepartmentProject

    def test_func(self):
        user = self.request.user

        return user.groups.filter(name__in=required_groups).exists() or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponse("You are not authorized to be here...please turn back")

    def get(self, request, *args, **kwargs):
        if 'change_target_status' in request.GET:
            target_id = request.GET['target_id']
            state = request.GET['state']

            if state in ['Not Started', 'In Progress', 'Completed', 'Pending Approval', 'Reject']:

                target = ProjectTarget.objects.get(id=target_id)

                if state == 'Reject':
                    target.state = 'Not Started'
                else:
                    target.state = state
                target.date = timezone.now()

                project = DepartmentProject.objects.get(id=kwargs['pk'])
                project.update_current_status_of_project_target()

                target.save()

                return JsonResponse({'confirm': True}, safe=False)
            else:
                return JsonResponse({'confirm': False}, safe=False)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        category = self.kwargs['department']

        context['page'] = 'Project'
        context['category'] = category

        context['title'] = title
        context['project_title'] = project_title
        context['user'] = user
        context['now'] = timezone.now()

        department = Department.objects.get(department_name=category)
        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

        context['department'] = department



        try:
            department_member = DepartmentMember.objects.get(member_name=user, department_name=department)
            context['department_membership'] = department_member
            context['is_department_leader'] = department.is_leader(department_member)
        except DepartmentMember.DoesNotExist:
            context['is_department_leader'] = False

        if user.is_superuser:
            context['member_departments'] = Department.objects.all()
        else:
            context['member_departments'] = Department.objects.get_member_departments(user)
        context['department_leaders'] = Department.objects.department_leaders()

        context['department_categories'] = DepartmentCategory.objects.get_department_categories(department)
        context['department_members'] = DepartmentMember.objects.get_department_members(department)

        return context

    def post(self, request, *args, **kwargs):

        department_project = self.get_object()

        form_submission_type = request.POST.get('form-submission')

        if not form_submission_type:
            return JsonResponse({'confirm': False}, safe=False, status=400)

        try:
            with transaction.atomic():

                if form_submission_type == 'edit-target':
                    self._edit_target(request)

                elif form_submission_type == 'add-target':
                    self._add_target(request, department_project)

                elif form_submission_type == 'edit-project':
                    self._edit_project(request, department_project)

                elif form_submission_type == 'manage-members':
                    self._manage_members(request, department_project)

                elif form_submission_type == 'delete-project':
                    return self._delete_project(department_project)

                elif form_submission_type == 'add-target':
                    self._add_target(request, department_project)

                elif form_submission_type == 'manage-target':
                    pass

        except Exception as e:
            return JsonResponse({'confirm': False, 'error': str(e)}, safe=False, status=400)
        return HttpResponseRedirect(reverse_lazy('project_management:project-detail', args=[department_project.department.department_name, department_project.id]))

    def _edit_target(self, request):
        edit_target_id = request.POST.get('edit-target-id')
        edit_target_title = request.POST.get('edit-target-title').strip()
        edit_target_description = request.POST.get('edit-target-description').strip()
        edit_target_due_date = request.POST.get('edit-target-due-date')

        project_target = ProjectTarget.objects.get(id=edit_target_id)
        project_target.target_name = edit_target_title if edit_target_title else project_target.target_name
        project_target.target_description = edit_target_description if edit_target_description else project_target.target_description
        project_target.due_date = edit_target_due_date if edit_target_due_date else project_target.due_date

        project_target.save()

    def _add_target(self, request, department_project):
        """Helper method to handle 'add-target' submission"""
        target_title = request.POST['target-title']
        target_description = request.POST['target-description']
        target_state = request.POST['target-state']
        target_due_date = request.POST['target-due-date']

        project_target = ProjectTarget.objects.create(
            target_name=target_title,
            target_description=target_description,
            state=target_state,
            due_date=target_due_date,
            project=department_project
        )

        department_project.target.add(project_target)
        department_project.save()

    def _edit_project(self, request, department_project):
        project_name = request.POST['project-name']
        project_status = request.POST['project-status']
        project_priority = request.POST['project-priority']
        project_description = request.POST['project-description']
        project_due_date = request.POST['project-due-date']
        project_background_color = request.POST['project-background-color']
        project_text_color = request.POST['project-text-color']

        department_project.project_name = project_name
        department_project.project_description = project_description
        department_project.project_priority = project_priority
        department_project.status = project_status
        department_project.due_date = project_due_date
        department_project.project_background_color = project_background_color
        department_project.project_text_color = project_text_color

        department_project.save()

    def _manage_members(self, request, department_project):

        department_members = request.POST.getlist('department_members')
        project_leader = request.POST.get('project_leader')

        members = [
            DepartmentMember.objects.get(id=mem_id, department_name=department_project.department)
            for mem_id in department_members
        ]

        project_leader = DepartmentMember.objects.get(id=project_leader, department_name=department_project.department)

        department_project.project_members.add(*members)
        department_project.project_leader = project_leader
        department_project.save()

    def _delete_project(self, department_project):
        """Helper method to handle 'delete-project' submission."""
        # department_name = department_project.department.department_name  # Get department name before deletion
        department_project.delete()

        return HttpResponseRedirect(reverse_lazy('project_management:project'))

    def _add_target(self, request, department_project):
        target_name = request.POST['target-title']
        target_description = request.POST['target-description']
        target_due_date = request.POST['target-due-date']

        project_target = ProjectTarget.objects.create(
            target_name=target_name,
            target_description=target_description,
            project=department_project,
            due_date=target_due_date,
        )

        department_project.target.add(project_target)

    def _manage_targets(self, request, department_project):
        pass


class ProjectManagementSettingView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/app/user-profile.html'

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=required_groups).exists() or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponse("You are not authorized to be here...please turn back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        # get all users
        all_users = CustomUser.objects.all()
        context['all_users'] = all_users

        user_leader_in_dept = Department.objects.filter(
            Q(leader__member_name=user) | Q(sub_leader__member_name=user)
        )
        context['user_leader_in_dept'] = user_leader_in_dept

        category = kwargs.get('diakonate', None)
        mode = None
        if category is None:  # project/settings/
            if user.is_superuser:
                user_diaconates = Diaconate.objects.all()

            elif user.groups.filter(name='Diakonate Head').exists():
                user_diaconates = Diaconate.objects.filter(Q(head=user) | Q(assistant=user))

            elif user.groups.filter(name='Department Head').exists():

                user_diaconates = Diaconate.objects.filter(
                    Q(department__leader__member_name=user) | Q(department__sub_leader__member_name=user)
                ).distinct()

                # context['user_leader_in_dept'] = user_leader_in_dept

            context['diaconates'] = user_diaconates
        else:
            mode = 'Diakonate'
            sub_category = kwargs.get('department', None)
            diaconate = Diaconate.objects.get(name=category)

            if sub_category is None:  # # project/settings/diakonate/
                # In the diakonate zone, where diakonate leaders can add departments
                # But a diakonate leader should be allowed to add department in the place
                # where they are the leader and not have the ability to add department in other
                # diakonate

                if user.is_superuser:
                    user_diaconates = Diaconate.objects.all()

                elif user.groups.filter(name='Diakonate Head').exists():
                    user_diaconates = Diaconate.objects.filter(Q(head=user) | Q(assistant=user))

                elif user.groups.filter(name='Department Head').exists():
                    user_diaconates = Diaconate.objects.filter(
                        Q(department__leader__member_name=user) | Q(department__sub_leader__member_name=user)
                    )
                    # user_leader_in_dept = Department.objects.filter(
                    #     Q(leader__member_name=user) | Q(sub_leader__member_name=user)
                    # )
                    # cont

                context['diaconates'] = user_diaconates

            else:
                mode = 'Department'

                department = Department.objects.get(department_name=sub_category)
                context['department'] = department
                unit_category = kwargs.get('unit', None)

                if unit_category is None:  # project/settings/diakonate/department/
                    if user.is_superuser:
                        pass
                    elif user.groups.filter(name='Diakonate Head').exists():
                        pass
                    elif user.groups.filter(name='Department Head').exists():
                        pass
                else:  # project/settings/diakonate/department/unit
                    mode = 'Unit'
                    context['unit'] = unit_category

                    unit = Unit.objects.get(id=unit_category)
                    context['unit'] = unit

            context['diaconate'] = diaconate

        context['mode'] = mode

        if user.is_superuser:
            context['member_departments'] = Department.objects.all()
        elif user.groups.filter(name='Diakonate Head').exists():
            department_queryset = Department.objects.filter(department_diaconate__in=user_diaconates)
            context['member_departments'] = department_queryset
        elif user.groups.filter(name='Department Head').exists():
            user_departments = Department.objects.filter(Q(leader__member_name=user) | Q(sub_leader__member_name=user))
            context['member_departments'] = user_departments


        # context['category'] = category
        context['project_title'] = project_title
        context['user'] = user

        # department = Department.objects.get(department_name=category)
        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

        # context['department'] = department
        #
        # if user.is_superuser:
        #     context['member_departments'] = Department.objects.all()
        # else:
        #     context['member_departments'] = Department.objects.get_member_departments(user)
        #
        # context['department_leaders'] = Department.objects.department_leaders()

        # context['department_projects'] = DepartmentProject.objects.filter(department=department).order_by('-start_date')
        # context['department_categories'] = DepartmentCategory.objects.get_department_categories(department)
        # context['department_members'] = DepartmentMember.objects.get_department_members(department)
        # context['department_units'] = department.unit_set.all()

        # family_members not in the department
        # context['family_members'] = [
        #     f"{brethren.get_full_name()} @{brethren.username}" for brethren in get_user_model().objects.exclude(
        #         username__in=[member.member_name.username for member in context['department_members']]
        #     )
        # ]
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if 'delete_department_membership' in request.POST:
            try:
                with transaction.atomic():
                    member_id = request.POST['delete_department_membership']
                    department_member = DepartmentMember.objects.get(id=member_id)
                    department_member.delete()

                    return HttpResponseRedirect(reverse_lazy(
                        'project_management:project-settings-diakonate-department',
                        args=[kwargs.get('diakonate'), kwargs.get('department')])
                    )
            except Exception as e:
                context['delete_error'] = str(e)
                return self.render_to_response(context)


        elif 'update_diakonate' in request.POST:
            diakonate = request.POST['update_diakonate']
            diakonate = Diaconate.objects.get(id=diakonate)

            diakonate_name = request.POST.get('diakonate-name', '').strip()
            diakonate_description = request.POST.get('diakonate-description', '').strip()
            diakonate_leader  = request.POST.get('diakonate-leader', '').strip()
            diakonate_assistant = request.POST.get('diakonate-assistant', '').strip()

            try:
                with transaction.atomic():
                    if diakonate_name:
                        diakonate.name = diakonate_name
                    if diakonate_description:
                        diakonate.info = diakonate_description
                    if diakonate_leader:
                        diakonate.leader = CustomUser.objects.get(username=diakonate_leader)
                    if diakonate_assistant:
                        diakonate.assistant = CustomUser.objects.get(username=diakonate_assistant)

                    diakonate.save()
                return HttpResponseRedirect(reverse_lazy(
                    'project_management:project-settings-diakonate',
                    args=[diakonate_name])
                )
            except Exception as e:
                context['update_error'] = str(e)
                return self.render_to_response(context)

        elif 'update_department' in request.POST:
            department = request.POST['update_department']
            department = Department.objects.get(id=department)

            department_full_name = request.POST.get('department-full-name', '').strip()
            department_name = request.POST.get('department-name', '').strip()
            department_objective = request.POST.get('department-objective', '').strip()
            department_head = request.POST.get('department-head', '').strip()
            department_assistant = request.POST.get('department-head-assistant', '').strip()

            try:
                with transaction.atomic():
                    if department_full_name:
                        department.department_long_name = department_full_name
                    if department_name:
                        department.department_name = department_name
                    if department_objective:
                        department.department_objectives = department_objective
                    if department_head:
                        department.leader = DepartmentMember.objects.get(member_name__username=department_head, department_name=department)
                    if department_assistant:
                        department.sub_leader = DepartmentMember.objects.get(member_name__username=department_assistant, department_name=department)
                    department.save()

                return HttpResponseRedirect(reverse_lazy(
                    'project_management:project-settings-diakonate-department',
                    args=[kwargs.get('diakonate'), department_name])
                )

            except Exception as e:
                context['update_error'] = str(e)
                return self.render_to_response(context)


        elif 'update_unit' in request.POST:
            unit = request.POST['update_unit']
            unit = Unit.objects.get(id=unit)

            unit_name = request.POST.get('unit-name', '').strip()
            unit_objective = request.POST.get('unit-objective', '').strip()
            unit_head = request.POST.get('unit-head', '').strip()
            unit_sub_leader = request.POST.get('unit-head-assistant', '').strip()

            try:
                with transaction.atomic():
                    if unit_name:
                        unit.name = unit_name
                    if unit_objective:
                        unit.objective = unit_objective
                    if unit_head:
                        unit.unit_leader = DepartmentMember.objects.get(id=unit_head)
                    if unit_sub_leader:
                        unit.sub_leader = DepartmentMember.objects.get(id=unit_sub_leader)
                    unit.save()


                return HttpResponseRedirect(reverse_lazy(
                    'project_management:project-settings-diakonate-department-unit',
                    args=[kwargs.get('diakonate'), kwargs.get('department'), unit.id])
                )
            except Exception as e:
                context['update_error'] = str(e)
                return self.render_to_response(context)

        elif 'delete_diaconate' in request.POST:
            mode = 'Diakonate'
            diaconate_id = request.POST['delete_diaconate']
            diaconate = Diaconate.objects.get(id=diaconate_id)
            diaconate.delete()

            return HttpResponseRedirect(reverse_lazy('project_management:project-settings'))

        elif 'delete_department' in request.POST:
            mode = 'Department'
            department_id = request.POST['delete_department']
            department = Department.objects.get(id=department_id)
            department.delete()

            return HttpResponseRedirect(reverse_lazy(
                'project_management:project-settings-diakonate',
                args=[kwargs.get('diakonate')])
            )

        elif 'delete_unit' in request.POST:
            mode = 'Unit'
            unit_id = request.POST['delete_unit']
            unit = Unit.objects.get(id=unit_id)
            unit.delete()

            return HttpResponseRedirect(reverse_lazy(
                'project_management:project-settings-diakonate-department',
                args=[kwargs.get('diakonate'), kwargs.get('department')])
            )

        else:
            form_submission_type = request.POST.get('form-submission-type', None)

            try:
                with transaction.atomic():
                    if form_submission_type is None:
                        diakonate_name = request.POST.get('diakonate-name', None)
                        diakonate_description = request.POST.get('diakonate-description', None)
                        diakonate_leader = request.POST.get('diakonate-leader', None)
                        diakonate_assistant = request.POST.get('diakonate-assistant', None)

                        diakonate_leader = CustomUser.objects.get(username=diakonate_leader)
                        diakonate_assistant = CustomUser.objects.get(username=diakonate_assistant) if diakonate_assistant else None

                        diakonate = Diaconate.objects.create(
                            name=diakonate_name,
                            info=diakonate_description,
                            head=diakonate_leader,
                            assistant=diakonate_assistant,
                        )

                    elif form_submission_type == 'Diakonate':
                        department_name = request.POST.get('department-name', None)
                        department_abridged_name = request.POST.get('department-abridged-name', None)
                        department_objective = request.POST.get('department-objective', None)

                        department_head = request.POST.get('department-head', None)
                        department_head_assistant = request.POST.get('department-head-assistant', None)

                        department_diakonate_name = kwargs.get('diakonate', None)
                        department_diakonate_name = Diaconate.objects.get(name=department_diakonate_name)

                        department = Department.objects.create(
                            department_name=department_abridged_name,
                            department_long_name=department_name,
                            department_objectives=department_objective,
                            department_diaconate=department_diakonate_name
                        )

                        department_head = DepartmentMember.objects.create(
                            member_name=CustomUser.objects.get(username=department_head),
                            department_name=department,
                        )
                        department.leader = department_head
                        department.member_names.add(department_head)

                        if department_head_assistant:
                            department_head_assistant = DepartmentMember.objects.create(
                                member_name=CustomUser.objects.get(username=department_head_assistant),
                                department_name=department
                            )
                            department.assistant = department_head_assistant
                            department.member_names.add(department_head_assistant)

                        department.save()

                        # add the department to the diakonate
                        department_diakonate_name.departments.add(department)

                    elif form_submission_type == 'Department':
                        form_submission_category = request.POST.get('form-submission-category', None)
                        diakonate = kwargs.get('diakonate', None)
                        department = kwargs.get('department', None)

                        diakonate = Diaconate.objects.get(name=diakonate)
                        department = Department.objects.get(department_name=department)

                        if form_submission_category == 'unit':

                            unit_name = request.POST.get('unit-name', None)
                            unit_objective = request.POST.get('unit-objective', None)

                            unit_head = request.POST.get('unit-head', None)
                            unit_head_assistant = request.POST.get('unit-head-assistant', None)

                            unit = Unit.objects.create(
                                name=unit_name,
                                objective=unit_objective,
                                unit_department=department,
                            )

                            if unit_head:
                                unit_head = department.member_names.get(member_name=unit_head)
                                unit.members.add(unit_head)

                            if unit_head_assistant:
                                unit_head_assistant = department.member_names.get(member_name=unit_head_assistant)
                                unit.members.add(unit_head_assistant)

                        elif form_submission_category == 'member':
                            new_member = request.POST.get('new-member', None)
                            new_member = CustomUser.objects.get(username=new_member)
                            unit = request.POST.get('member-unit', None)

                            # check if new member already exist in the department
                            member = DepartmentMember.objects.filter(
                                member_name=new_member,
                                department_name=department,
                            )

                            if member.exists():
                                new_member = member.first()
                            else:
                                new_member = DepartmentMember.objects.create(
                                    member_name=new_member,
                                    department_name=department,
                                )

                                department.member_names.add(new_member)

                            if unit:
                                unit = department.unit_set.get(id=unit)
                                unit.members.add(new_member)

                    elif form_submission_type == 'Unit':
                        form_submission_category = request.POST.get('form-submission-category', None)

                        diakonate = kwargs.get('diakonate', None)
                        department = kwargs.get('department', None)
                        unit = kwargs.get('unit', None)

                        diakonate = Diaconate.objects.get(name=diakonate)
                        department = Department.objects.get(department_name=department)
                        unit = department.unit_set.get(id=unit)

                        if form_submission_category == 'subunit':
                            pass
                        elif form_submission_category == 'member':
                            new_unit_member = request.POST.get('new-member', None)
                            new_unit_member = CustomUser.objects.get(username=new_unit_member)

                            member = DepartmentMember.objects.filter(
                                member_name=new_unit_member,
                                department_name=department,
                            )

                            if member.exists():
                                new_unit_member = member.first()
                            else:
                                new_unit_member = DepartmentMember.objects.create(
                                    member_name=new_unit_member,
                                    department_name=department
                                )
                                department.member_names.add(new_unit_member)

                            unit.members.add(new_unit_member)

            except Exception as e:
                JsonResponse({'confirm': False, 'error': str(e)}, status=400)

            if form_submission_type is None:
                return HttpResponseRedirect(reverse_lazy('project_management:project-settings'))
            elif form_submission_type == 'Diakonate':
                return HttpResponseRedirect(reverse_lazy('project_management:project-settings-diakonate', args=[kwargs.get('diakonate')]))
            elif form_submission_type == 'Department':
                return HttpResponseRedirect(reverse_lazy('project_management:project-settings-diakonate-department', args=[kwargs.get('diakonate'), kwargs.get('department')]))

        return HttpResponseRedirect(reverse_lazy(
            'project_management:project-settings-diakonate-department-unit',
            args=[kwargs.get('diakonate'), kwargs.get('department'), kwargs.get('unit')])
        )


class ProjectManagementAdminSettingView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/app/admin_setting.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'
                or self.request.user.is_superuser):

            if 'update_department' in request.GET:
                admin_mode = request.GET['admin_mode']
                department_name = request.GET['department_name']
                new_value = request.GET.get('new_value', None)

                department = Department.objects.get(department_name=department_name)

                if new_value:
                    if admin_mode == 'update_department_long_name':
                        new_value = new_value.replace("'", "’")
                        department.department_long_name = new_value
                    elif admin_mode == 'update_department_name':
                        department.department_name = new_value
                    elif admin_mode == 'update_department_leader':
                        leader = get_user_model().objects.get(id=new_value)

                        try:
                            leader = DepartmentMember.objects.get(member_name=leader, department_name=department)
                        except DepartmentMember.DoesNotExist:
                            leader = DepartmentMember(
                                member_name=leader,
                                department_name=department
                            )
                            leader.save()
                        department.leader = leader

                        if leader not in department.member_names.all():
                            department.member_names.add(leader)

                    elif admin_mode == 'update_department_sub_leader':
                        sub_leader = get_user_model().objects.get(id=new_value)

                        try:
                            sub_leader = DepartmentMember.objects.get(member_name=sub_leader,
                                                                      department_name=department)
                        except DepartmentMember.DoesNotExist:
                            sub_leader = DepartmentMember(
                                member_name=sub_leader,
                                department_name=department
                            )
                            sub_leader.save()
                        department.sub_leader = sub_leader

                        if sub_leader not in department.member_names.all():
                            department.member_names.add(sub_leader)

                    elif admin_mode == 'update_department_objective':
                        department.department_objectives = new_value

                    try:
                        department.save()
                    except Exception as e:
                        err_msg = str(e)

                        return JsonResponse({'confirm': False, 'err_msg': err_msg})

                    if admin_mode == 'update_department_leader':
                        new_value = department.leader.member_name.get_full_name()
                    elif admin_mode == 'update_department_sub_leader':
                        new_value = department.sub_leader.member_name.get_full_name()

                    return JsonResponse({'confirm': True, 'value': new_value})

            elif 'delete_department' in request.GET:
                department_name = request.GET.get('department_name', None)

                department = Department.objects.get(department_name=department_name)
                department.delete()

                return JsonResponse({'confirm': True})

            elif 'delete_member' in request.GET:
                department_member = request.GET.get('member_name', None)
                department_name = request.GET.get('department_name')

                department = Department.objects.get(department_name=department_name)
                department_member = DepartmentMember.objects.get(id=department_member)

                # if department_member.member_name.username == department.leader.username:

                department.member_names.remove(department_member)
                department_member.delete()

                return JsonResponse({'confirm': True})
            
            elif 'delete_category' in request.GET:
                department_category = request.GET.get('category_name', None)
                department_name = request.GET.get('department_name')

                department = Department.objects.get(department_name=department_name)
                department_category = DepartmentCategory.objects.get(id=department_category)

                department.department_categories.remove(department_category)
                department_category.delete()

                return JsonResponse({'confirm': True})

            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not Authorized to come here...please Go Back!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        context['project_title'] = project_title
        context['user'] = user
        context['page'] = 'Settings'

        context['departments'] = Department.objects.all()
        context['potential_leaders'] = get_user_model().objects.all()

        context['member_departments'] = Department.objects.all()

        context['family_members'] = [
            f"{brethren.get_full_name()} @{brethren.username}" for brethren in context['potential_leaders']
        ]

        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)
        context['Diaconate'] = Diaconate.objects.all()

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        settings = request.GET.get('settings', None)

        if settings == 'add_diaconate':
            diaconate_name = request.POST['diaconate_name']
            diaconate_info = request.POST['diaconate_info']

            # TODO: Confirm which level the user must be to qualify for leadership
            diaconate_head = request.POST['diaconate_head']
            diaconate_head = get_user_model().objects.get(pk=diaconate_head)

            diaconate_assistant = request.POST['diaconate_assistant']
            diaconate_assistant = get_user_model().objects.get(pk=diaconate_assistant)

            try:
                diaconate = Diaconate.objects.create(
                    name=diaconate_name, info=diaconate_info,
                    head=diaconate_head, assistant=diaconate_assistant
                )
            except IntegrityError as e:
                if request.htmx:
                    context['status'] = False
                    context['error_message'] = f"{diaconate_name} already exist"
                    context['category'] = settings

                    return render(request, 'project_management/partial_html/add_diaconate.html', context)
                else:
                    return HttpResponseRedirect(reverse_lazy('project_management:project-admin-settings'))

            if request.htmx:
                context['status'] = True
                context['counter'] = Diaconate.objects.count()
                context['office'] = diaconate
                context['category'] = settings
                return render(request, 'project_management/partial_html/add_diaconate.html', context)

        elif settings == 'add_department':
            try:
                with transaction.atomic():
                    diaconate_name = request.POST['department_diaconate_name']
                    diaconate = Diaconate.objects.get(name=diaconate_name)

                    department_name = request.POST['department_name'].replace("'", '’')
                    department_short_name = request.POST['department_short_name']
                    department_objective = request.POST['department_objective']

                    # TODO: Confirm which level the user must be to qualify for leadership
                    department_leader = request.POST['department_leader']
                    department_leader = get_user_model().objects.get(pk=department_leader)

                    department_sub_leader = request.POST['department_sub_leader']
                    department_sub_leader = get_user_model().objects.get(pk=department_sub_leader)

                    # create department instance on the database
                    department = Department.objects.create(
                        department_diaconate=diaconate,
                        department_name=department_short_name,
                        department_long_name=department_name,
                    )

                    # add department to diaconate
                    diaconate.departments.add(department)

                    department_leader = DepartmentMember.objects.create(
                        member_name=department_leader,
                        department_name=department
                    )

                    department_sub_leader = DepartmentMember.objects.create(
                        member_name=department_sub_leader,
                        department_name=department
                    )

                    # add the leaders to the department
                    department.leader = department_leader
                    department.sub_leader = department_sub_leader
                    department.save()

                    department.member_names.add(department_leader, department_sub_leader)

                    # create department category instance and add to the department
                    department_category = request.POST['department_category'].strip()

                    if department_category:
                        department_category = department_category.split(',')
                        department_category = [
                            DepartmentCategory.objects.create(
                                category_name=name,
                                department_name=department
                            ) for name in department_category
                        ]
                        department.department_categories.add(*department_category)

                    # Create Department member instances and add them to the department
                    new_members = request.POST['family_members']
                    new_members = [member.strip() for member in new_members.split(',') if member]

                    if new_members:
                        new_members = [
                            DepartmentMember.objects.create(
                                member_name=get_user_model().objects.get_user_from_full_name(name),
                                department_name=department
                            ) for name in new_members if name
                        ]
                        department.member_names.add(*new_members)

                    if request.htmx:
                        context['status'] = True
                        context['department'] = department
                        context['category'] = settings
                        return render(request, 'project_management/partial_html/add_department.html', context)

                return HttpResponseRedirect(reverse_lazy('project_management:project-admin-settings'))
            except IntegrityError as e:
                if request.htmx:
                    context['status'] = False
                    context['error_message'] = f"{request.POST.get('department_short_name')} already exist"
                    context['category'] = settings

                    return render(request, 'project_management/partial_html/add_department.html', context)
                else:
                    return HttpResponseRedirect(reverse_lazy('project_management:project-admin-settings'))
        
        elif settings == 'delete_diaconate':
            diaconate_id = request.POST['diaconate_id']
            diaconate = Diaconate.objects.get(id=diaconate_id)
            diaconate.delete()

        return HttpResponseRedirect(reverse_lazy('project_management:project-admin-settings'))


class ProjectManagementAdminSettingDepartmentDetailView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/app/department_detail_admin.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'
                or self.request.user.is_superuser):
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden('You are not Authorized to come here...please God back')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['project_title'] = project_title
        context['user'] = user
        context['page'] = 'Settings'

        context['potential_leaders'] = get_user_model().objects.all()
        context['member_departments'] = Department.objects.all()
        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

        department = kwargs['pk']
        department = Department.objects.get(id=department)
        context['department'] = department

        context['family_members'] = [user for user in get_user_model().objects.all() if not department.is_member(user)]

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        settings = request.GET.get('settings', None)
        department = kwargs['pk']
        department = Department.objects.get(id=department)

        if settings == 'add_category':
            category_name = request.POST['category_name']
            category_objective = request.POST['category_objective']

            # check to see if category is already in the department
            # in case the admin made the mistake of creating the same category
            category = DepartmentCategory.objects.filter(category_name=category_name, department_name=department)

            # create department category instance

            if not category:
                category = DepartmentCategory.objects.create(
                    category_name=category_name,
                    department_name=department,
                    category_objective=category_objective
                )
                # add category to the department
                department.department_categories.add(category)

                # check if request is a partial request
                if request.htmx:
                    context['status'] = True
                    context['department_category'] = category
                    context['category'] = settings
                    context['department'] = department

                    return render(request, 'project_management/partial_html/add_category.html', context)
            else:
                if request.htmx:
                    context['status'] = False
                    context['category'] = settings
                    context['error_message'] = f"{category_name} already exist"
                    return render(request, 'project_management/partial_html/add_category.html', context)

        elif settings == 'add_department_member':
            new_member_name = request.POST['new_member_name']
            member_user = get_user_model().objects.get(pk=new_member_name)

            # add user to department member instance
            if not department.is_member(member_user):

                department_member = DepartmentMember.objects.create(
                    member_name=member_user,
                    department_name=department
                )
                department.member_names.add(department_member)

                if request.htmx:
                    context['status'] = True
                    context['member'] = department_member
                    context['category'] = settings
                    context['department'] = department
                    return render(request, 'project_management/partial_html/add_member.html', context)
            else:
                if request.htmx:
                    context['status'] = False
                    context['category'] = settings
                    context['error_message'] = f"{member_user.get_full_name()} is already a member"
                    return render(request, 'project_management/partial_html/add_member.html', context)

        elif settings == 'update_member_details':
            department_name = request.POST['update_department_name']
            abridged_department_name = request.POST['update_department_name_abridge']
            
            leader_name = request.POST['update_leaders_name']
            try:
                leader_name = DepartmentMember.objects.get(member_name__id=leader_name, department_name=department)
            except DepartmentMember.DoesNotExist:
                leader_name = DepartmentMember.objects.create(
                    member_name=get_user_model().objects.get(id=leader_name),
                    department_name=department
                )
                department.member_names.add(leader_name)

            assistant_leader_name = request.POST['update_assistant_leaders_name']
            try:
                assistant_leader_name = DepartmentMember.objects.get(member_name__id=assistant_leader_name, department_name=department)
            except DepartmentMember.DoesNotExist:
                assistant_leader_name = DepartmentMember.objects.create(
                    member_name=get_user_model().objects.get(id=assistant_leader_name),
                    department_name=department
                )
                department.member_names.add(assistant_leader_name)

            department_objective = request.POST['update_department_objective']

            department.department_name = abridged_department_name
            department.department_long_name = department_name
            department.leader = leader_name
            department.sub_leader = assistant_leader_name
            department.department_objectives = department_objective

            department.save()

            if request.htmx:
                context['status'] = True
                context['category'] = settings
                context['department'] = department
                return render(request, 'project_management/partial_html/update_department_details.html', context)

        elif settings == 'delete_category':
            department_category = request.POST.get('category_pk', None)
            department_category = DepartmentCategory.objects.get(pk=department_category)

            department.department_categories.remove(department_category)
            department_category.delete()

            return JsonResponse({}, safe=True)

        elif settings == 'delete_member':
            department_member = request.POST.get('department_member_pk', None)
            department_member = DepartmentMember.objects.get(pk=department_member)

            # if it is a leader that has been removed, remove the leader from position
            if department_member == department.leader:
                department.leader = None
                department.save()
            elif department_member == department.sub_leader:
                department.sub_leader = None
                department.save()

            department_member.delete()
            
            return JsonResponse({}, safe=True)
        
        elif settings == 'delete_department':
            diaconate = department.department_diaconate

            # diaconate.departments.remove(department)
            department.delete()

            return HttpResponseRedirect(reverse_lazy('project_management:project-admin-settings'))

        return HttpResponseRedirect(
            reverse_lazy(
                'project_management:project-admin-setting-department-detail',
                args=[department.department_name, department.id]
            )
        )


class DepartmentProjectCalenderView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/project-calender.html'

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=required_groups).exists() or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponse("You are not authorized to be here...please turn back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        category = self.kwargs['department']

        context['page'] = 'Calendar'
        context['category'] = category

        context['project_title'] = project_title
        context['user'] = user

        department = Department.objects.get(department_name=category)
        context['department'] = department

        if user.is_superuser:
            context['member_departments'] = Department.objects.all()
        else:
            context['member_departments'] = Department.objects.get_member_departments(user)

        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

        return context


class DepartmentTableDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    login_url = reverse_lazy('users-login')
    template_name = "project_management/project-department-tables-detail.html"
    model = DepartmentTable

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=required_groups).exists() or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponse("You are not authorized to be here...please turn back")

    def get(self, request, *args, **kwargs):
        if 'table_row_id' in request.GET:

            table_row_id = request.GET['table_row_id']

            table = self.get_object()
            row = table.row_values.get(id=table_row_id)

            for value in row.table_field_value.all():
                value.delete()

            row.delete()

            return JsonResponse({})
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        user = self.request.user
        category = self.kwargs['department']

        context['page'] = 'Dashboard'
        context['category'] = category

        context['title'] = title
        context['project_title'] = project_title
        context['user'] = user

        department = Department.objects.get(department_name=category)
        context['department'] = department

        if user.is_superuser:
            context['member_departments'] = Department.objects.all()
        else:
            context['member_departments'] = Department.objects.get_member_departments(user)

        context['department_leaders'] = Department.objects.department_leaders()

        # GET Member Activity in the project
        members, complete_project = department.member_activity_in_a_department()
        context['member_activity_in_a_department'] = zip(members, complete_project)

        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

        family_member = get_user_model().objects.exclude(level='chief_shep')
        context['family_member'] = family_member

        return context

    def post(self, request, *args, **kwargs):
        # Now in this dynamic database we don't have any
        # idea what is going to be in the POST request

        department = kwargs['department']
        pk = kwargs['pk']
        database_table = self.get_object()

        if 'download_custom_database' in request.POST:
            table_fields = database_table.fields.all()

            data_records = {
                field.name: list(field.values.all().values_list('value', flat=True)) for field in table_fields 
            }
            response = convert_to_format(data_records, f"{database_table.table_name}", 'excel')

            return response

        database_action = request.POST['database_action']

        if database_action == 'add_row':
            table_fields = database_table.fields.all()

            field_values = []
            for field in table_fields:
                if field.field_type == 'file':
                    # Do the upload here
                    files = request.FILE.get(field.name, None)

                    if files:
                        files = ''
                    else:
                        pass
                elif field.field_type == 'family_member':
                    field.foreign_key = 'Family Member'

                    fam_username = request.POST[field.name]
                    fam = get_user_model().objects.get(username=fam_username).get_full_name()

                    value = FieldValue(value=fam, custom_field=field)

                else:
                    value = FieldValue(
                        value=request.POST[field.name],
                        custom_field=field
                    ) 
                value.save()

                # add value to this field
                field.values.add(value)

                field_values.append(value)

            field_value_index = FieldValueIndex.objects.create(
                department_table_name=database_table
            )

            field_value_index.table_field_value.add(*field_values)
            database_table.row_values.add(field_value_index)

        elif database_action == 'edit_row':
            row_id = request.POST['row_id']

            field_value_index = database_table.row_values.get(id=row_id)

            for field_value in field_value_index.table_field_value.all():
                field_value.value = request.POST[field_value.custom_field.name]
                field_value.save()

        return HttpResponseRedirect(reverse_lazy('project_management:project-department-table-detail', args=kwargs.values()))


class ProjectMemberView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = "project_management/project-member-list.html"

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=required_groups).exists() or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponse("You are not authorized to be here...please turn back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        context['page'] = 'Member'
        context['title'] = title
        context['project_title'] = project_title
        context['user'] = user

        user_leader_in_dept = Department.objects.filter(
            Q(leader__member_name=user) | Q(sub_leader__member_name=user)
        )
        context['user_leader_in_dept'] = user_leader_in_dept

        if user.is_superuser:
            user_diaconates = Diaconate.objects.all()
            context['diaconates'] = user_diaconates
        elif user.groups.filter(name="Diakonate Head").exists():
            user_diaconates = Diaconate.objects.filter(Q(head=user) | Q(assistant=user))
            context['diaconates'] = user_diaconates
        elif user.groups.filter(name='Department Head').exists():
            user_diaconates = Diaconate.objects.filter(department__in=user_leader_in_dept).distinct()
            context['diaconates'] = user_diaconates

        return context


class DepartmentMemberDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    login_url = reverse_lazy('users-login')
    template_name = "project_management/project-member-detail.html"
    model = DepartmentMember

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=required_groups).exists() or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponse("You are not authorized to be here...please turn back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        context['title'] = title
        context['project_title'] = project_title
        context['user'] = user



        context['user_departments'] = DepartmentMember.objects.get_user_departments(self.request.user)
        user_department_members = self.request.user.departmentmember_set.all()

        context['user_departments_members'] = user_department_members

        return context

    def post(self, request, *args, **kwargs):
        pass

