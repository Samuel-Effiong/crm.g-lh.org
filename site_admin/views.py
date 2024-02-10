from typing import Any
from django.urls import reverse_lazy

from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden

from evangelism.models import Evangelism
from church_work.models import ChurchWork
from personal_development.models import (
    BibleReading, PrayerMarathon, ShepherdReport
)

from users.models import (
    CustomUser, SubShepherd, Shepherd, FamilyMemberWeeklySchedule
)


developers = "God's Lighthouse Developers Team (GDevT)"
title = 'GLH-FAM'


# Create your views here.
class SiteAdminView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/site_admin/admin.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Only Admins allowed here")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['category'] = 'Homepage'
        context['developer'] = developers
        context['user'] = self.request.user
        context['title'] = f"Site Admin | {title}"
        return context


class SiteAdminListView(LoginRequiredMixin, ListView):

    login_url = reverse_lazy('users-login')
    template_name = 'project_management/site_admin/admin_list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        if self.kwargs['sub_category'] == 'users':
            queryset = CustomUser.objects.all()
        elif self.kwargs['sub_category'] == 'sub_shepherd':
            queryset = SubShepherd.objects.all()
        elif self.kwargs['sub_category'] == 'shepherd':
            queryset = Shepherd.objects.all()
        elif self.kwargs['sub_category'] == 'members_schedule':
            queryset = FamilyMemberWeeklySchedule.objects.all()
        elif self.kwargs['sub_category'] == 'evangelisms':
            queryset = Evangelism.objects.all()
        # elif self.kwargs['category'] ==

        return queryset

    def get(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Only Admins allowed here")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['sub_category'] = self.kwargs['sub_category'].replace('_', " ").title()
        context['developer'] = developers
        context['user'] = self.request.user
        context['title'] = f"Select {context['sub_category']} to change | {title}"

        return context


class SiteAdminDetailView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/site_admin/admin_detail.html'
    context_object_name = 'object_detail'

    def get_object(self, queryset=None):
        primary_key = self.kwargs['pk']
        category = self.kwargs['sub_category']

        if category == 'users':
            obj = CustomUser.objects.get(pk=primary_key)
        elif category == 'sub_shepherd':
            obj = SubShepherd.objects.get(pk=primary_key)
        elif category == 'shepherd':
            obj = Shepherd.objects.get(pk=primary_key)
        elif category == 'members_schedule':
            obj = FamilyMemberWeeklySchedule.objects.get(pk=primary_key)
        elif category == 'evangelisms':
            obj = Evangelism.objects.all()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['sub_category'] = self.kwargs['sub_category'].replace('_', " ").title()
        context['developer'] = developers
        context['user'] = self.request.user
        context['title'] = f"Select {context['sub_category']} to change | {title}"

        if context['sub_category'] == 'Sub Shepherd':
            context['sub_shepherd'] = SubShepherd.objects.all()
        elif context['sub_category'] == 'Shepherd':
            context['shepherd'] = Shepherd.objects.all()
        elif context['sub_category'] == 'Members Schedule':
            context['members_schedule'] = FamilyMemberWeeklySchedule.objects.all()
        return context
