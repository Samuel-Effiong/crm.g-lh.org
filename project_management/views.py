from typing import Any, Dict
from datetime import datetime

from django.db import models

from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils import timezone
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


title = 'GLH-FAM'
project_title = 'GLH-PROJ'


def is_member(user):
    member = DepartmentMember.objects.filter(member_name=user)
    return len(member) > 0


class ProjectManagementView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/index.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'
                or is_member(self.request.user)):
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

                # Get the department the user in and select the first
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
        project_name = request.POST['project_name']
        project_description = request.POST['project_description']
        category = request.POST['category']
        due_date = request.POST['due_date']
        members = request.POST.getlist('members')

        department = Department.objects.get(department_name=department_name)
        members = [DepartmentMember.objects.get(member_name__username=mem, department_name=department) for mem in members]
        department_category = DepartmentCategory.objects.get(category_name=category, department_name=department)

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

            elif settings == 'member':
                family_members = request.POST.get('family_members', None).strip()

                if family_members:
                    family_member_list = [member for member in family_members.split(',') if member]

                    new_members = [
                        DepartmentMember.objects.create(
                            member_name=get_user_model().objects.get_user_from_full_name(name),
                            department_name=department
                        )
                        for name in family_member_list if name
                    ]
                    department.member_names.add(*new_members)

            elif settings == 'remove_member':
                removed_member = request.POST.get('removed_member', None).strip()

                if removed_member:
                    department_member = DepartmentMember.objects.get(id=removed_member)
                    department.member_names.remove(department_member)

                    department_member.delete()

            elif settings == 'remove_category':
                removed_category = request.POST.get('removed_category', None).strip()

                if removed_category:
                    department_category = DepartmentCategory.objects.get(id=removed_category)
                    department.department_categories.remove(department_category)

                    department_category.delete()

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


class ProjectManagementAdminSettingView3(LoginRequiredMixin, TemplateView):
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
                            sub_leader = DepartmentMember.objects.get(member_name=sub_leader, department_name=department)
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

        context['departments'] = Department.objects.all()
        context['potential_leaders'] = get_user_model().objects.all()

        context['member_departments'] = Department.objects.all()

        context['family_members'] = [
            f"{brethren.get_full_name()} @{brethren.username}" for brethren in context['potential_leaders']
        ]

        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

        return context

    def post(self, request, *args, **kwargs):
        admin_mode = request.POST['admin_mode']

        if admin_mode != 'add_department':
            department_name = request.POST['department_name']
            department = Department.objects.get(department_name=department_name)

        if admin_mode == 'add_department':
            department_long_name = request.POST['long_name'].replace("'", "’")
            department_short_name = request.POST['short_name']
            department_objective = request.POST['department_objective']

            department_leader = request.POST['department_leader']
            department_leader = get_user_model().objects.get(pk=department_leader)

            department_sub_leader = request.POST['department_sub_leader']
            department_sub_leader = get_user_model().objects.get(pk=department_sub_leader)

            department = Department(
                department_name=department_short_name,
                department_long_name=department_long_name,
                department_objectives=department_objective
            )
            department.save()

            # Add the leaders and sub leader to the department
            department_leader = DepartmentMember(
                member_name=department_leader,
                department_name=department
            )
            department_leader.save()

            department_sub_leader = DepartmentMember(
                member_name=department_sub_leader,
                department_name=department
            )
            department_sub_leader.save()

            # Add them to the department
            department.leader = department_leader
            department.sub_leader = department_sub_leader
            department.save()

            department.member_names.add(department_leader, department_sub_leader)

            # Create department category instance and add to the department
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
                        department_name=department)
                    for name in new_members if name
                ]

                department.member_names.add(*new_members)
                
        elif admin_mode == 'add_category':
            category_name = request.POST['category_name']
            category_objective = request.POST['category_objective']
            
            # create department category instance
            department_category = DepartmentCategory(
                category_name=category_name,
                department_name=department,
                category_objective=category_objective
            )
            department_category.save()
            
            # add category to the department
            department.department_categories.add(department_category)
            
        elif admin_mode == 'add_member':
            new_member_name = request.POST['new_member_name']

            member_user = get_user_model().objects.get(pk=new_member_name)

            # add user to department member instance
            department_member = DepartmentMember(
                member_name=member_user,
                department_name=department
            )
            department_member.save()
            department.member_names.add(department_member)

        return HttpResponseRedirect(reverse_lazy('project_management:project-admin-settings'))


class ProjectManagementAdminSettingView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/app/admin_setting2.html'

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
        admin_mode = request.POST['admin_mode']

        if admin_mode != 'add_department':
            department_name = request.POST['department_name']
            department = Department.objects.get(department_name=department_name)

        if admin_mode == 'add_department':
            department_long_name = request.POST['long_name'].replace("'", "’")
            department_short_name = request.POST['short_name']
            department_objective = request.POST['department_objective']

            department_leader = request.POST['department_leader']
            department_leader = get_user_model().objects.get(pk=department_leader)

            department_sub_leader = request.POST['department_sub_leader']
            department_sub_leader = get_user_model().objects.get(pk=department_sub_leader)

            department = Department(
                department_name=department_short_name,
                department_long_name=department_long_name,
                department_objectives=department_objective
            )
            department.save()

            # Add the leaders and sub leader to the department
            department_leader = DepartmentMember(
                member_name=department_leader,
                department_name=department
            )
            department_leader.save()

            department_sub_leader = DepartmentMember(
                member_name=department_sub_leader,
                department_name=department
            )
            department_sub_leader.save()

            # Add them to the department
            department.leader = department_leader
            department.sub_leader = department_sub_leader
            department.save()

            department.member_names.add(department_leader, department_sub_leader)

            # Create department category instance and add to the department
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
                        department_name=department)
                    for name in new_members if name
                ]

                department.member_names.add(*new_members)

        elif admin_mode == 'add_category':
            category_name = request.POST['category_name']
            category_objective = request.POST['category_objective']

            # create department category instance
            department_category = DepartmentCategory(
                category_name=category_name,
                department_name=department,
                category_objective=category_objective
            )
            department_category.save()

            # add category to the department
            department.department_categories.add(department_category)

        elif admin_mode == 'add_member':
            new_member_name = request.POST['new_member_name']

            member_user = get_user_model().objects.get(pk=new_member_name)

            # add user to department member instance
            department_member = DepartmentMember(
                member_name=member_user,
                department_name=department
            )
            department_member.save()
            department.member_names.add(department_member)

        return HttpResponseRedirect(reverse_lazy('project_management:project-admin-settings'))


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

        database_action = request.POST['database_action']
        database_table = self.get_object()

        department = kwargs['department']
        pk = kwargs['pk']

        if database_action == 'add_row':
            table_fields = database_table.fields.all()

            field_values = []
            for field in table_fields:
                if field.field_type == 'file':
                    # Do the upload here
                    files = request.FILE.get(field.name, None)

                    if files:
                        files = '';
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



