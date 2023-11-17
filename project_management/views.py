from typing import Any, Dict
from datetime import datetime

from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect, JsonResponse

from .models import (Department, DepartmentMember, DepartmentCategory,
                     DepartmentProject, ProjectTarget)

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
            return super().get(request, *args, **kwargs)

        return HttpResponseRedirect("You are not Authorized to come here...please Go Back!")

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        user = self.request.user

        context['category'] = 'Dashboard'
        context['title'] = title
        context['user'] = user
        context['project_title'] = project_title

        context['member_departments'] = Department.objects.get_member_departments(user)
        context['department_leaders'] = Department.objects.department_leaders()

        return context


class DepartmentProjectListView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/project-index.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'
                or is_member(self.request.user)):
            return super().get(request, *args, **kwargs)
        return HttpResponseRedirect("You are not Authorized to come here...please Go Back!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        category = kwargs['department']

        context['category'] = category
        context['title'] = title
        context['project_title'] = project_title
        context['user'] = user

        department = Department.objects.get(department_name=category)

        context['department'] = department
        context['member_departments'] = Department.objects.get_member_departments(user)
        context['department_leaders'] = Department.objects.department_leaders()

        context['department_projects'] = DepartmentProject.objects.filter(department=department)
        context['department_categories'] = DepartmentCategory.objects.get_department_categories(department)
        context['department_members'] = DepartmentMember.objects.get_department_members(department)
        context['is_department_leader'] = department.is_leader(user)

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

                if state in ['Not Started', 'In Progress', 'Completed', 'Pending Approval']:

                    target = ProjectTarget.objects.get(id=target_id)
                    target.state = state
                    target.date = timezone.now()
                    target.save()

                    return JsonResponse({'confirm': True}, safe=False)
                else:
                    return JsonResponse({'confirm': False}, safe=False)

            return super().get(request, *args, **kwargs)
        return HttpResponseRedirect("You are not Authorized to come here...please Go Back!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        category = self.kwargs['department']

        context['category'] = category
        context['title'] = title
        context['project_title'] = project_title
        context['user'] = user
        context['now'] = timezone.now()

        department = Department.objects.get(department_name=category)

        context['department'] = department
        context['member_departments'] = Department.objects.get_member_departments(user)
        context['department_leaders'] = Department.objects.department_leaders()

        context['department_categories'] = DepartmentCategory.objects.get_department_categories(department)
        context['department_members'] = DepartmentMember.objects.get_department_members(department)

        context['is_department_leader'] = department.is_leader(user)

        return context

    def post(self, request, *args, **kwargs):
        # context = self.get_context_data(**kwargs)

        department_project = DepartmentProject.objects.get(id=kwargs['pk'])

        project_name = request.POST['project_name']
        project_description = request.POST['project_description']
        project_category = request.POST['project_category']
        project_start_date = request.POST['project_start_date']
        project_due_date = request.POST['project_due_date']

        project_members = request.POST['project_members']
        project_members = project_members.split('~')

        project_targets = request.POST['project_targets']
        project_targets = project_targets.split('~')

        department_project.project_name = project_name
        department_project.project_description = project_description
        department_project.department_category = DepartmentCategory.objects.get(category_name=project_category, department_name=department_project.department)
        department_project.start_date = project_start_date
        department_project.due_date = project_due_date

        department_project.project_members.clear()
        department_project.project_members.add(*[DepartmentMember.objects.get(id=pk) for pk in project_members])

        # In updating the targets list, do not delete those that is already
        # in the database that the department leader decides to keep, instead remove
        # those tha is in the database but isn't in the leader updated list

        deleted_target = ProjectTarget.objects.exclude(target_name__in=project_targets, project=department_project)
        deleted_target.delete()

        # insert those that are not in it [the new list]
        for target_name in project_targets:
            target = ProjectTarget.objects.filter(target_name=target_name, project=department_project)
            if not target:
                new_target = ProjectTarget(target_name=target_name, project=department_project, state="Not Started")
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
        return HttpResponseRedirect("You are not Authorized to come here...please Go Back!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        category = self.kwargs['department']

        context['category'] = category
        context['project_title'] = project_title
        context['user'] = user

        department = Department.objects.get(department_name=category)

        context['department'] = department
        context['member_departments'] = Department.objects.get_member_departments(user)
        context['department_leaders'] = Department.objects.department_leaders()

        context['department_projects'] = DepartmentProject.objects.filter(department=department).order_by('-start_date')
        context['department_categories'] = DepartmentCategory.objects.get_department_categories(department)
        context['department_members'] = DepartmentMember.objects.get_department_members(department)

        # family_members not in the department
        context['family_members'] = [
            brethren.get_full_name() for brethren in get_user_model().objects.exclude(
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
                    family_members_list = [member for member in family_members.split(',') if member]

                    # add family member to department list
                    department_member = []

                    for fam in family_members_list:
                        # retrieve the user object of the fam using their names
                        first_name, last_name = fam.title().split()
                        fam_user = get_user_model().objects.get(first_name=first_name, last_name=last_name)

                        # Join the member to the department member table
                        new_department_member = DepartmentMember(member_name=fam_user, department_name=department)
                        new_department_member.save()

                        # add user to the department itself table
                        department.member_names.add(new_department_member)

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
        return HttpResponseRedirect(reverse_lazy('project_management:project-settings', args=[department]))
