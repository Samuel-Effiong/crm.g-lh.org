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
        context['member_departments'] = Department.objects.get_member_departments(user)

        context['department_projects'] = DepartmentProject.objects.filter(department__department_name=category)
        context['department_categories'] = DepartmentCategory.objects.get_department_categories(category)
        context['department_members'] = DepartmentMember.objects.get_department_members(category)

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

                if state in ['Not Started', 'Pending', 'Completed']:

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

        context['member_departments'] = Department.objects.get_member_departments(user)
        context['department_categories'] = DepartmentCategory.objects.get_department_categories(category)
        context['department_members'] = DepartmentMember.objects.get_department_members(category)

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

        # department_project.target.clear()
        # ProjectTarget.objects.filter(project=department_project).delete()

        # department_project.target.all().delete()

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

        context['department'] = Department.objects.get(department_name=category)
        context['member_departments'] = Department.objects.get_member_departments(user)

        context['department_projects'] = DepartmentProject.objects.filter(department__department_name=category)
        context['department_categories'] = DepartmentCategory.objects.get_department_categories(category)
        context['department_members'] = DepartmentMember.objects.get_department_members(category)

        return context

