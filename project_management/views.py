from typing import Any, Dict
from datetime import datetime

import pandas as pd

from django_htmx.http import HttpResponseClientRedirect

from django.db import models, transaction, IntegrityError

from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils import timezone
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.http import (HttpResponseRedirect, JsonResponse,
                         HttpResponseForbidden, HttpResponse)

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


title = 'GLH-FAM'
project_title = 'GLH-PROJ'


def is_member(user):
    """A utitlity function to check is a user belongs to any department"""
    member = DepartmentMember.objects.filter(member_name=user)
    return len(member) > 0


class ProjectManagementView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/index.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'
                or is_member(self.request.user),
                ):
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
                    member_department = Department.objects.first()

                    if not member_department:
                        return HttpResponseRedirect(reverse_lazy('project_management:project-admin-settings'))
                else:
                    member_department = Department.objects.get_member_departments(request.user)

                    if not member_department:
                        return HttpResponseForbidden("Please Join A Department before you can access this page.")
                    else:
                        member_department = member_department[0]

                department_dashboard = member_department.department_name
                return HttpResponseRedirect(reverse_lazy('project_management:department_dashboard', args=[department_dashboard]))

        return HttpResponseForbidden("You are not Authorized to come here...please Go Back!")

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        user = self.request.user

        context['category'] = kwargs['department']

        context['page'] = 'Dashboard'

        context['title'] = title
        context['user'] = user
        context['project_title'] = project_title
        context['department_name'] = f"{kwargs['department']} Dashboard"

        department = Department.objects.get(department_name=context['category'])
        context['department'] = department

        # Context needed to handle the navigation
        if user.is_superuser:
            context['member_departments'] = Department.objects.all()
        else:
            context['member_departments'] = Department.objects.get_member_departments(user)
        context['department_leaders'] = [leader.member_name for leader in Department.objects.department_leaders() if leader]

        try:
            department_member = DepartmentMember.objects.get(member_name=user, department_name=department)
            context['department_membership'] = department_member
            context['is_department_leader'] = department.is_leader(department_member)
        except DepartmentMember.DoesNotExist:
            context['is_department_leader'] = False

        department_projects = DepartmentProject.objects.filter(department=department, status__in=['In Progress', 'Not Started'])
        context['department_projects'] = department_projects

        department_projects_status_statistic = DepartmentProject.objects.get_department_projects_status_statistic(department)
        context['department_project_status_statistic'] = department_projects_status_statistic

        all_department_pending_target = ProjectTarget.objects.all_department_pending_target(department)
        context['all_department_pending_target'] = all_department_pending_target

        # GET Member Activity in the project
        members, complete_project = department.member_activity_in_a_department()
        context['member_activity_in_a_department'] = zip(members, complete_project)

        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

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

        pass


class DepartmentProjectListView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/project-index.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'
                or is_member(self.request.user)):
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not Authorized to come here...please Go Back!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        category = kwargs['department']

        context['page'] = 'Project'
        context['category'] = category

        context['title'] = title
        context['project_title'] = project_title
        context['user'] = user

        department = Department.objects.get(department_name=category)

        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

        context['department'] = department
        try:
            department_member = DepartmentMember.objects.get(member_name=user, department_name=department)
            context['department_membership'] = department_member
        except DepartmentMember.DoesNotExist:
            # To be able to get here, must be a super user
            pass

        if user.is_superuser:
            context['member_departments'] = Department.objects.all()
        else:
            context['member_departments'] = Department.objects.get_member_departments(user)

        context['department_leaders'] = Department.objects.department_leaders()

        department_projects = DepartmentProject.objects.filter(department=department)
        if 'filter' in self.request.GET:
            status = self.request.GET['status']
            priority = self.request.GET['priority']

            if status != 'All':
                department_projects = department_projects.filter(status=status)
            if priority != 'All':
                department_projects = department_projects.filter(project_priority=priority)

            context['filter_by_status'] = status
            context['filter_by_priority'] = priority
        else:
            context['filter_by_status'] = 'All'
            context['filter_by_priority'] = 'All'

        context['department_projects'] = department_projects

        context['department_categories'] = DepartmentCategory.objects.get_department_categories(department)
        context['department_members'] = DepartmentMember.objects.get_department_members(department)

        try:
            context['is_department_leader'] = department.is_leader(department_member)
        except UnboundLocalError:
            # Must be a super user to activate this error
            context['is_department_leader'] = False

        return context

    def post(self, request, *args, **kwargs):
        department_name = kwargs['department']
        project_name = request.POST.get('project_name', None)
        project_description = request.POST.get('project_description', None)
        category = request.POST.get('category', None)
        due_date = request.POST.get('due_date', None)
        members = request.POST.getlist('members')
        unit = request.POST.get('units', None)
        use_units_toggle_button = request.POST.get('use_units_toggle_button', None)

        department = Department.objects.get(department_name=department_name)

        if not use_units_toggle_button:
            members = [DepartmentMember.objects.get(member_name__username=mem, department_name=department) for mem in members]
        else:
            if unit:
                unit = Unit.objects.get(id=unit)
                members = unit.members.all()

        
        department_category = DepartmentCategory.objects.get(category_name=category, department_name=department) if category else None    

        department_project = DepartmentProject.objects.create(
            department=department,
            project_name=project_name,
            project_description=project_description,
            department_category=department_category,
            due_date=due_date
        )
        department_project.project_members.add(*members)
        return HttpResponseRedirect(reverse_lazy('project_management:project', args=[department_name]))


class DepartmentProjectDetailView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/project-detail.html'
    model = DepartmentProject

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'
                or is_member(self.request.user)):

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
        return HttpResponseForbidden("You are not Authorized to come here...please Go Back!")

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
        # context = self.get_context_data(**kwargs)

        department_project = DepartmentProject.objects.get(id=kwargs['pk'])

        project_name = request.POST['project_name']
        project_description = request.POST['project_description']
        project_category = request.POST['project_category']
        project_start_date = request.POST['project_start_date']
        project_due_date = request.POST['project_due_date']

        project_priority = request.POST['project_priority']
        project_leader = request.POST['project_leader']

        project_background_color = request.POST['project_background_color']
        project_text_color = request.POST['project_text_color']

        project_members = request.POST['project_members']
        project_members = project_members.split('~')

        project_targets = request.POST['project_targets']
        project_targets = project_targets.split('~')
        project_targets = [target.strip() for target in project_targets if target]

        department_project.project_name = project_name
        department_project.project_description = project_description
        department_project.department_category = DepartmentCategory.objects.get(category_name=project_category, department_name=department_project.department)
        department_project.start_date = project_start_date
        department_project.due_date = project_due_date

        department_project.project_priority = project_priority
        department_project.project_background_color = project_background_color
        department_project.project_text_color = project_text_color
        department_project.project_leader = DepartmentMember.objects.get(id=project_leader)

        department_project.project_members.clear()
        department_project.project_members.add(*[DepartmentMember.objects.get(id=pk) for pk in project_members])

        if department_project.project_leader not in department_project.project_members.all():
            department_project.project_leader = None

        # In updating the targets list, do not delete those that is already
        # in the database that the department leader decides to keep, instead remove
        # those tha is in the database but isn't in the leader updated list

        department_project_targets = ProjectTarget.objects.filter(project=department_project)

        # Delete all the target that is not preserved in the updated target list
        preserved_target = []
        for target in department_project_targets:
            if target.target_name not in project_targets:
                department_project.target.remove(target)
                target.delete()

        # Add the new target to the department_project
        for target in project_targets:
            test_target = department_project_targets.filter(target_name=target)

            if not test_target:
                new_target = ProjectTarget(target_name=target, project=department_project)
                new_target.save()
                department_project.target.add(new_target)
    
        department_project.save()
        return JsonResponse({'confirm': True}, safe=False)


class ProjectManagementSettingView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/app/user-profile.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'
                or is_member(self.request.user)):

                if 'mode' in request.GET:
                    department = kwargs['department']
                    department = Department.objects.get(department_name=department)
                    context = {}

                    if request.GET['mode'] == 'display_unit_member':
                        pk = request.GET['unit_pk']

                        try:
                            department_unit = Unit.objects.get(pk=pk)
                            context['status'] = True
                            context['department'] = department
                            context['department_unit'] = department_unit

                        except Unit.DoesNotExist as e:
                            context['status'] = False    
                        return render(request, 'project_management/app/partial_html/display_unit_members.html', context)
                    
                    elif request.GET['mode'] == 'remove_unit_member':
                        department_unit = request.GET['department_unit_pk']
                        member = request.GET['member_pk']
                    
                        try:
                            department_unit = Unit.objects.get(pk=department_unit)
                            member = DepartmentMember.objects.get(pk=member)
                            department_unit.members.remove(member)

                            context['status'] = True
                        except (Unit.DoesNotExist, DepartmentMember.DoesNotExist):
                            context['status'] = False

                        return HttpResponse({})
                    elif request.GET['mode'] == 'display_unit_leader':
                        unit_pk = request.GET['unit_pk']

                        department_unit = Unit.objects.get(pk=unit_pk)
                        context['status'] = True
                        context['department_unit'] = department_unit

                        return render(request, 'project_management/app/partial_html/display_unit_leader.html', context)
                    
                return super().get(request, *args, **kwargs)
                
        return HttpResponseForbidden("You are not Authorized to come here...please Go Back!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        category = self.kwargs['department']

        context['category'] = category
        context['project_title'] = project_title
        context['user'] = user

        department = Department.objects.get(department_name=category)
        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

        context['department'] = department

        if user.is_superuser:
            context['member_departments'] = Department.objects.all()
        else:
            context['member_departments'] = Department.objects.get_member_departments(user)

        context['department_leaders'] = Department.objects.department_leaders()

        context['department_projects'] = DepartmentProject.objects.filter(department=department).order_by('-start_date')
        context['department_categories'] = DepartmentCategory.objects.get_department_categories(department)
        context['department_members'] = DepartmentMember.objects.get_department_members(department)
        context['department_units'] = department.unit_set.all()

        # family_members not in the department
        context['family_members'] = [
            f"{brethren.get_full_name()} @{brethren.username}" for brethren in get_user_model().objects.exclude(
                username__in=[member.member_name.username for member in context['department_members']]
            )
        ]

        return context

    def post(self, request, *args, **kwargs):
        settings = request.GET.get('settings', None)
        department = kwargs['department']
        department = Department.objects.get(department_name=department)

        if settings is not None:
            if settings == 'category':
                category_name = request.POST.get('category_name', None).strip()
                category_objective = request.POST.get('category_objective').strip()

                if category_name:
                    category = DepartmentCategory(category_name=category_name,
                                                  category_objective=category_objective,
                                                  department_name=department
                                                  )
                    category.save()
                    department.department_categories.add(category)

            if settings == 'unit':
                unit_name = request.POST.get('unit_name', None).strip()
                unit_objective = request.POST.get('unit_objective').strip()

                unit_leader = request.POST.get('unit_leader', None)
                if unit_leader:
                    unit_leader = DepartmentMember.objects.get(id=unit_leader)

                unit_members = request.POST.getlist('unit_members')

                if unit_members:
                    unit_members = [DepartmentMember.objects.get(id=member) for member in unit_members if int(member) != unit_leader.pk]

                try:
                    with transaction.atomic():
                        department_unit = Unit.objects.create(
                            name=unit_name,
                            unit_leader=unit_leader,
                            objective=unit_objective,
                            unit_department=department
                        )
                        if unit_leader:
                            department_unit.members.add(unit_leader)
                        if unit_members:
                            department_unit.members.add(*unit_members)

                except IntegrityError as e: 
                    pass

            elif settings == 'member':
                family_members = request.POST.get('family_members', None).strip()

                if family_members:
                    family_member_list = [member for member in family_members.split(',') if member]
                    try: 
                        with transaction.atomic():
                            new_members = [
                                DepartmentMember.objects.create(
                                    member_name=get_user_model().objects.get_user_from_full_name(name),
                                    department_name=department
                                )
                                for name in family_member_list if name
                            ]
                            department.member_names.add(*new_members)
                    except IntegrityError as e:
                        pass

            elif settings == 'remove_member':
                removed_member = request.POST.get('removed_member', None).strip()

                if removed_member:
                    department_member = DepartmentMember.objects.get(id=removed_member)

                    if department.leader == department_member:
                        department.leader = None
                    elif department.sub_leader == department_member:
                        department.sub_leader = None

                    department_member.delete()

            elif settings == 'remove_category':
                removed_category = request.POST.get('removed_category', None).strip()

                if removed_category:
                    department_category = DepartmentCategory.objects.get(id=removed_category)
                    department_category.delete()

            elif settings == 'remove_unit':
                removed_unit = request.POST.get('removed_unit', None).strip()

                if removed_unit:
                    department_unit = Unit.objects.get(id=removed_unit)
                    department_unit.delete()

            elif settings == 'add_unit_member':
                # Partial Html
                department_unit = request.POST.get('unit_to_add_member')
                department_unit = Unit.objects.get(pk=department_unit)

                member = request.POST.get('add_member_to_unit')

                if member:
                    member = DepartmentMember.objects.get(pk=member)

                    if not department_unit.members.contains(member):
                        department_unit.members.add(member)

                context = {
                    'status': True,
                    'department': department,
                    'department_unit': department_unit
                }

                return render(request, 'project_management/app/partial_html/display_unit_members.html', context)

            elif settings == 'update_unit_information':
                unit_pk = request.POST.get('update_unit_pk', None)
                unit = Unit.objects.get(id=unit_pk)

                new_name = request.POST.get('display_unit_name', None)
                new_objective = request.POST.get('display_unit_objective', None)

                new_leader = request.POST.get('display_unit_leader', None)
                new_leader = DepartmentMember.objects.get(id=new_leader)
                context = {}

                try:
                    with transaction.atomic():

                        unit.name = new_name
                        unit.objective = new_objective
                        unit.unit_leader = new_leader

                        unit.save()
                except IntegrityError as e:
                    message = str(e)
                    context['status'] = False
                    context['failure_message'] = message
                else:
                    context['status'] = True
                    context['unit'] = unit
                    context['department'] = department

                return render(request, 'project_management/app/partial_html/update_unit.html', context)

            elif settings == 'experience_score':
                department_member = request.POST.get('experience_id', None)

                if department_member:
                    department_member = DepartmentMember.objects.get(id=department_member)

                    try:
                        new_experience_score = int(request.POST.get('experience_score', None))
                    except (TypeError, ValueError) as e:
                        pass
                    else:
                        department_member.experience_score = new_experience_score
                        department_member.save()
        return HttpResponseRedirect(reverse_lazy('project_management:project-settings', args=[department.department_name]))


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

            # if it is a leader that is been removed, remove the leader from position
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


class DepartmentProjectCalenderView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/project-calender.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'
                or is_member(self.request.user)):

            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not Authorized to come here...please Go Back!")

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


class DepartmentTableDetailView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('users-login')
    template_name = "project_management/project-department-tables-detail.html"
    model = DepartmentTable 

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'
                or is_member(self.request.user)):

            if 'table_row_id' in request.GET:

                table_row_id = request.GET['table_row_id']
                
                table = self.get_object()
                row = table.row_values.get(id=table_row_id)

                for value in row.table_field_value.all():
                    value.delete()

                row.delete()

                return JsonResponse({})
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not Authorized to come here...please Go Back!")
    
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




