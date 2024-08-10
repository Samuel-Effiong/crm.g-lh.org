from typing import Any
from datetime import datetime
from django.urls import reverse_lazy

from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.db import IntegrityError, transaction


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

        if 'status' in self.request.GET and 'message' in self.request.GET:
            status = self.request.GET['status']
            message = self.request.GET['message']

            context['status'] = True if status == 'True' else False
            context['message'] = message
            context['uploaded'] = self.request.GET.get('upload', False)

        if self.kwargs['sub_category'] == 'shepherd' or self.kwargs['sub_category'] == 'sub_shepherd':
            fam_members = CustomUser.objects.all()
            context['fam_members'] = fam_members

        return context
    
    def post(self, request, *args, **kwargs):
        category = kwargs['category']
        sub_category = kwargs['sub_category']

        if sub_category == 'users':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            phone_number = request.POST['phone_number']
            gender = request.POST['gender']

            try:            
                with transaction.atomic():

                    new_user = CustomUser.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        username=username,
                        email=email,
                        phone_number=phone_number,
                        gender=gender
                    )

                    new_user.set_password(password)
                    new_user.save()
            except IntegrityError as e:
                return HttpResponseRedirect(f"{reverse_lazy('site_admin:admin-category', args=[kwargs['category'], kwargs['sub_category']])}?status=True&message={str(e)}&upload=failed")

        elif sub_category == 'shepherd' or sub_category == 'sub_shepherd':
            name = request.POST['name']
            no_of_sheep = request.POST['no_of_sheep']
            date_of_appointment = request.POST['date_of_appointment']
            callings = request.POST['callings']

            try:
                with transaction.atomic():
                    if sub_category == 'shepherd':
                        shepherd = Shepherd.objects.create(
                            name=CustomUser.objects.get(id=name),
                            no_of_sheep=no_of_sheep,
                            date_of_appointment=datetime.fromisoformat(date_of_appointment),
                            callings=callings
                        )

                    elif sub_category == 'sub_shepherd':
                        sub_shepherd = SubShepherd.objects.create(
                            name=CustomUser.objects.get(id=name),
                            no_of_sheep=no_of_sheep,
                            date_of_appointment=date_of_appointment,
                            callings=callings
                        )
            except IntegrityError as e:
                return HttpResponseRedirect(f"{reverse_lazy("site_admin:admin-category", args=[kwargs['category'], kwargs['sub_category']])}?status=True&message={str(e)}&upload=failed")

        elif sub_category == 'members_schedule':
            pass

        return HttpResponseRedirect(f"{reverse_lazy('site_admin:admin-category', args=[kwargs['category'], kwargs['sub_category']])}?status=True&message=Successfully added to the database&upload=success")

 
class SiteAdminDetailView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('users-login')
    template_name = 'project_management/site_admin/admin_detail.html'
    context_object_name = 'object_detail'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            if 'delete_action' in request.GET:
                object_detail = self.get_object()
                object_detail.delete()

                return HttpResponseRedirect(
                    reverse_lazy('site_admin:admin-category', 
                                 args=[self.kwargs['category'], kwargs['sub_category']]
                    )
                )
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Only Admins allowed here")

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

        if self.kwargs['sub_category'] == 'sub_shepherd':
            context['shepherd'] = SubShepherd.objects.all()
        elif self.kwargs['sub_category'] == 'shepherd':
            context['shepherd'] = Shepherd.objects.all()
        elif self.kwargs['sub_category'] == 'members_schedule':
            context['members_schedule'] = FamilyMemberWeeklySchedule.objects.all()

        if 'status' in self.request.GET and 'message' in self.request.GET:
            context['status'] = True if self.request.GET['status'] == 'True' else False
            context['message'] = self.request.GET['message']
            context['uploaded'] = self.request.GET['uploaded']
        return context
    
    def post(self, request, **kwargs):
        object_details = self.get_object()

        category = kwargs['category']
        sub_category = kwargs['sub_category']

        try:
            with transaction.atomic():
                if sub_category == 'users':
                    first_name = request.POST['first_name']
                    last_name = request.POST['last_name']
                    username = request.POST['username']
                    gender = request.POST['gender']
                    phone_number = request.POST['phone_number']
                    blood_group = request.POST['blood_group']
                    level = request.POST['level']

                    object_details.first_name = first_name
                    object_details.last_name = last_name
                    object_details.username = username
                    object_details.gender = gender
                    object_details.phone_number = phone_number
                    object_details.blood_group = blood_group
                    object_details.level = level

                    object_details.save()

                elif sub_category == 'shepherd' or sub_category == 'sub_shepherd':
                    name = request.POST['shepherd']
                    name = Shepherd.objects.get(id=name) if sub_category == 'shepherd' else SubShepherd.objects.get(id=name)
                    no_of_sheep = request.POST['no_of_sheep']
                    date_of_appointment = request.POST['date_of_appointment']
                    callings = request.POST['callings']
                    
                    object_details.name = name
                    object_details.no_of_sheep = no_of_sheep
                    object_details.date_of_appointment = date_of_appointment
                    object_details.callings = callings

                    object_details.save()
                elif sub_category == 'Members Schedule':
                    pass
        except IntegrityError as e:
            return HttpResponseRedirect(f'{request.get_full_path()}?status=False&message=Successfully updated Database&uploaded=failed')
        
        return HttpResponseRedirect(f'{request.get_full_path()}?status=True&message=Successfully updated Database&uploaded=success')
        
