from typing import Any, Dict

import os
import requests
import numpy as np
import pandas as pd
from random import choice
from datetime import datetime

from django import http
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.http import HttpRequest, HttpResponse

from django.views.generic.base import TemplateView, View
from django.db import IntegrityError, transaction

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from users.models import Shepherd, SubShepherd, CustomUser, Catalog, Skill, Course
from users.models import Permission
from users.my_models.users import LEVEL_CHOICES
from users.my_models.utilities import convert_to_format

from church_work.models import ChurchWork
from evangelism.models import Evangelism
from personal_development.models import BibleReading, PrayerMarathon, ShepherdReport
from prophetic_vision.models import PropheticVision

from home.models import Notification

from .models import (
    Testimony, PropheticWord, Blog, Sermon, 
    UrlShortener)

developers = "God's Lighthouse Developers Team (GDevT)"
title = 'GLH-FAM'

days = {
    'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6
}

months = {
    'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5,
    'Jul': 6, 'Aug': 7, 'Sept': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
}


def sort_function(series):
    val = series[0]
    if val in days.keys():
        rule = days
    elif val in months.keys():
        rule = months

    return series.apply(lambda x: rule[x])


def download_profiles_in_format(request, _format, data=None, filename=None):
    if _format == 'image':
        if request.user.level == 'chief_shep':
            if data is None:
                # We are in the shepherd dashboard
                data = CustomUser.objects.values_list('profile_pic', flat=True)
            else:
                # We are in the shepherd list view
                data = data.values_list('profile_pic', flat=True)

        elif request.user.level == 'core_shep':
            data = CustomUser.objects.get_shepherd_sheep(shepherd).values_list('profile_pic', flat=True)
        elif request.user.level == 'sub_shep':
            data = CustomUser.objects.get_sub_shepherd_sheep(shepherd).values_list('profile_pic', flat=True)

        response = convert_to_format(data, 'Profile Images', _format)

    else:
        fields = [
            'first_name', 'last_name', 'username', 'gender', 'date_of_birth',
            'about', 'phone_number', 'email', 'occupation', 'address', 'skills',
            'blood_group', 'genotype', 'chronic_illness', 'lga', 'state', 'country',
            'course_of_study', 'years_of_study', 'current_year_of_study', 'final_year_status',
            'next_of_kin_full_name', 'next_of_kin_relationship', 'next_of_kin_phone_number',
            'next_of_kin_address', 'gift_graces', 'callings', 'reveal_calling_by_shepherd',
            'unit_of_work', 'shepherd', 'sub_shepherd', 'last_active_date', 'shoe_size',
            'cloth_size', 'level'
        ]

        if request.user.level == 'chief_shep':
            if data is None:
                data = CustomUser.objects.values(*fields)
            else:
                data = data.values(*fields)
            filename = 'Sheep Profiles' if not filename else filename

        elif request.user.level == 'core_shep':
            shepherd = Shepherd.objects.get(name=request.user)
            data = CustomUser.objects.get_shepherd_sheep(shepherd).values(*fields)

            filename = f"{shepherd.get_shepherd_full_name()} Sheep Profiles"

        elif request.user.level == 'sub_shep':
            shepherd = SubShepherd.objects.get(name=request.user)
            data = CustomUser.objects.get_sub_shepherd_sheep(shepherd).values(*fields)

            filename = f"{shepherd.get_shepherd_full_name()} Sheep Profiles"

        response = convert_to_format(data, filename, _format)

    return response


# Create your views here.
class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/index.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep' or self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Dashboard'
        context['developers'] = developers
        context['user'] = self.request.user
        context['title'] = title

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        # TODO: Sort by sheep activeness
        user = self.request.user

        if user.level == 'core_shep' or user.level == 'chief_shep':
            shepherd = Shepherd.objects.get(name=user)
        elif user.level == 'sub_shep':
            shepherd = SubShepherd.objects.get(name=user)
        else:
            # if by mistake someone slips through
            return HttpResponseForbidden("How do you get here!")

        context['shepherd'] = shepherd

        if user.level == 'chief_shep':
            context['core_shepherd'] = Shepherd.objects.all().exclude(name=user)

            # Get the list and percentage of both gender
            female_list = get_user_model().objects.get_particular_field_value_only('gender', 'F')
            male_list = get_user_model().objects.get_particular_field_value_only('gender', 'M')

            total_female = len(female_list)
            total_male = len(male_list)

            total_gender = total_female + total_male

            context['female_list'] = female_list
            context['female_total'] = total_female

            context['male_list'] = male_list
            context['male_total'] = total_male

            context['total_gender'] = total_gender

            unique_skills, unique_counts, unique_percentage, users_with_skills, users_without_skills = get_user_model().objects.get_skills_categories_count()

            assert len(unique_skills) == len(unique_percentage)
            assert len(unique_counts) == len(unique_skills)

            context['unique_skills'] = zip(unique_skills, unique_counts, unique_percentage)

            context['users_with_skills'] = users_with_skills
            context['users_without_skills'] = users_without_skills

            context['total_users'] = users_with_skills + users_without_skills

        elif user.level == 'core_shep':
            context['sheep'] = get_user_model().objects.get_shepherd_sheep(shepherd=shepherd)
        elif user.level == 'sub_shep':
            context['sheep'] = get_user_model().objects.get_sub_shepherd_sheep(sub_shepherd=shepherd)

        return context

    def post(self, request, *args, **kwargs):

        # Process request to download users profile details
        if 'download_format' in request.GET:
            _format = request.POST['download_format']

            response = download_profiles_in_format(request, _format)

            return response
        return self.render_to_response({})


class ShepherdSheepListView(LoginRequiredMixin, TemplateView):
    """This view is exclusively for the Chief Shepherd to view the list of
    all the shepherds"""

    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/shepherd_sheep_list.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['category'] = 'Shepherd List'
        context['developers'] = developers

        shepherd = Shepherd.objects.get(id=kwargs['pk'])
        sheep = get_user_model().objects.get_shepherd_sheep(shepherd)

        context['shepherd'] = shepherd
        context['sheep'] = sheep

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        return context

    def post(self, request, *args, **kwargs):

        if 'download_format' in request.GET:
            _format = request.POST['download_format']

            if request.user.level == 'chief_shep':
                shepherd = Shepherd.objects.get(id=kwargs['pk'])
                data = get_user_model().objects.get_shepherd_sheep(shepherd)

                filename = f"{shepherd.get_shepherd_full_name()} Sheep profiles"

                response = download_profiles_in_format(request, _format, data, filename)
            else:  # This code ought not to ever progress to this point
                response = download_profiles_in_format(request, _format)

            return response
        return self.render_to_response({})


class SheepSummaryDetailView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/sheep_summary_details.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):

            if 'settings' in request.GET:
                try:
                    username = request.GET['username']
                    level = request.GET['level']

                    user = get_user_model().objects.get(username=username)

                    if level == 'sub_shep':
                        # check if user is already a subshepherd
                        sub_shepherd = SubShepherd.objects.filter(name=user)

                        if sub_shepherd:
                            # user is already a subshepherd, do nothing
                            return JsonResponse({'confirm': True})
                        else:
                            # check if user is core shepherd that you wish to lower
                            if user.level == 'core_shep':
                                # delete the user from the core shepherd database
                                Shepherd.objects.get(name=user).delete()
                                user.is_staff = False

                            # add the new sub shepherd to the sub shepherd database
                            sub_shepherd = SubShepherd(
                                name=user, no_of_sheep=0,
                                date_of_appointment=datetime.now(),
                                calling='unknown'
                            )
                            sub_shepherd.save()

                    elif level == 'core_shep':
                        # check if user is already a shepherd
                        core_shepherd = Shepherd.objects.filter(name=user)

                        if core_shepherd:
                            return JsonResponse({'confirm': True})
                        else:
                            # check if user is a sub shepherd that you wish to increase
                            if user.level == 'sub_shep':
                                # delete the user from the sub shepherd database
                                SubShepherd.objects.get(name=user).delete()

                            user.is_staff = True

                            core_shepherd = Shepherd(
                                name=user, no_of_sheep=0,
                                date_of_appointment=datetime.now(),
                                calling='unknown'
                            )

                            core_shepherd.save()

                    else:
                        if user.level == 'sub_shep':
                            SubShepherd.objects.get(name=user).delete()
                            user.is_stafff = False
                        elif user.level == 'core_shep':
                            Shepherd.objects.get(name=user).delete()
                            user.is_staff = False
                    user.level = level
                    user.save()
                except Exception as e:
                    return JsonResponse({'confirm': False, 'message': str(e)})
                return JsonResponse({'confirm': True})

            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Sheep Detail View'
        context['developers'] = developers
        context['user'] = self.request.user
        context['title'] = title

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        # Sometimes I do crazy stuff
        wannabe_shepherd = get_user_model().objects.get(username=kwargs['sheep'])

        if wannabe_shepherd.level == 'core_shep':
            context['shepherd'] = Shepherd.objects.get(name=wannabe_shepherd)
        else:
            shepherd = Shepherd.objects.get(name__username=kwargs['shepherd'])
            context['shepherd'] = shepherd

        sheep: CustomUser = get_user_model().objects.get(username=kwargs['sheep'])

        context['sheep'] = sheep
        context['church_work'] = sheep.churchwork_set.all().order_by('-date')
        context['field_mission'] = sheep.evangelism_set.all().order_by('no_of_people_prayed')
        context['bible_reading'] = sheep.biblereading_set.all().order_by('status')
        context['prayer_marathon'] = sheep.prayermarathon_set.all().order_by('-date')
        context['prophetic_vision'] = sheep.propheticvision_set.all().order_by('-date')

        context['level'] = LEVEL_CHOICES

        return context


class ProfileDetailView(LoginRequiredMixin, TemplateView):
    """Access the Sheep Profile Details with having ways of editing it"""
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/users-profile.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = 'Profile'
        context['title'] = title

        user = get_user_model().objects.get(username=kwargs['sheep'])
        context['user'] = user

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        return context


# FIXME: Not in use
class DetailView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/detail.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep' or self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category = kwargs['category']
        context['category'] = kwargs['category']
        context['title'] = title

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        user = get_user_model().objects.get(username=kwargs['sheep'])
        context['user'] = user

        pk = kwargs['pk']
        if category == 'Church Work':
            detail = ChurchWork.objects.get(username=user, id=pk)
        elif category == 'Evangelism':
            detail = Evangelism.objects.get(username=user, id=pk)
        elif category == 'Bible Reading':
            detail = BibleReading.objects.get(username=user, id=pk)
        elif category == 'Prayer Marathon':
            detail = PrayerMarathon.objects.get(username=user, id=pk)
        elif category == 'Prophetic Vision':
            detail = PropheticVision.objects.get(username=user, id=pk)
        elif category == 'Shepherd Report':
            detail = ShepherdReport.objects.get(username=user, id=pk)

        context['detail'] = detail

        return context


class ShepherdReportView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/shepherd_reports.html'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if 'chart_request' in request.GET:
            if request.user.level == 'core_shep':
                shepherd = Shepherd.objects.get(name=request.user)
                female_dates, male_dates = ShepherdReport.shepherd_manager.date_series(shepherd=shepherd)
            elif 'chief_shep_bypass' in request.GET:
                shepherd_username = request.GET['shepherd_username']
                shepherd = Shepherd.objects.get(name__username=shepherd_username)
                female_dates, male_dates = ShepherdReport.shepherd_manager.date_series(shepherd=shepherd)
            elif request.user.level == 'chief_shep':
                female_dates, male_dates = ShepherdReport.shepherd_manager.date_series()

            context = {'category': 'Sheep Report'}

            if not female_dates.empty and not male_dates.empty:  # IF BOTH MALE AND FEMALE DATA ARE PRESENT
                female_dates = female_dates.strftime('%a')
                male_dates = male_dates.strftime('%a')

                female_distinct_values, female_unique_counts = np.unique(female_dates, return_counts=True)
                male_distinct_values, male_unique_counts = np.unique(male_dates, return_counts=True)

                female_distinct_values = female_distinct_values.tolist()
                male_distinct_values = male_distinct_values.tolist()

                # Normalise the values across each sex, filling up the missiong data point
                distinct_values = list(set(female_distinct_values + male_distinct_values))
                female_counts, male_counts = [0] * len(distinct_values), [0] * len(distinct_values)

                for index, unique in enumerate(distinct_values):
                    try:
                        female_counts[index] = female_unique_counts[female_distinct_values.index(unique)]
                    except ValueError:
                        pass

                    try:
                        male_counts[index] = male_unique_counts[male_distinct_values.index(unique)]
                    except ValueError:
                        pass

                data = {
                    'distinct_values': distinct_values,
                    'female_counts': female_counts,
                    'male_counts': male_counts,
                }

                df = pd.DataFrame(data)

                df = df.sort_values(by='distinct_values', key=sort_function)

                context['distinct_values'] = df['distinct_values'].tolist()
                context['female_counts'] = df['female_counts'].tolist()
                context['male_counts'] = df['male_counts'].tolist()

                context['completeness'] = 'both'

            elif not male_dates.empty and female_dates.empty:  # IF ONLY MALE DATA IS PRESENT
                context['completeness'] = 'single'
                context['available_gender'] = 'Male'

                male_dates = male_dates.strftime('%a')
                male_distinct_values, male_unique_counts = np.unique(male_dates, return_counts=True)

                data = {
                    'distinct_values': male_distinct_values,
                    'unique_counts': male_unique_counts
                }

                df = pd.DataFrame(data)
                df = df.sort_values(by='distinct_values', key=sort_function)

                context['distinct_values'] = df['distinct_values'].tolist()
                context['unique_counts'] = df['unique_counts'].tolist()

            elif not female_dates.empty and male_dates.empty:
                context['completeness'] = 'single'
                context['available_gender'] = 'Female'

                female_dates = female_dates.strftime('%a')
                female_distinct_values, female_unique_counts = np.unique(female_dates, return_counts=True)

                data = {
                    'distinct_values': female_distinct_values,
                    'unique_counts': female_unique_counts
                }

                df = pd.DataFrame(data)
                df = df.sort_values(by='distinct_values', key=sort_function)

                context['distinct_values'] = df['distinct_values'].tolist()
                context['unique_counts'] = df['unique_counts'].tolist()

            return JsonResponse(context, safe=False)
        else:
            if self.request.user.is_staff and (
                    self.request.user.level == 'core_shep' or self.request.user.level == 'chief_shep'):
                return super().get(request, *args, **kwargs)
            return HttpResponseForbidden("You are not a shepherd...please go back")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['category'] = 'Shepherd Report'
        context['developers'] = developers
        context['user'] = user
        context['title'] = title

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        shepherd = Shepherd.objects.get(name=user)

        if 'chief_shep_bypass' in self.request.GET:
            chief_shep_bypass = True
            shepherd_username = self.request.GET['shepherd_username']
            shepherd = Shepherd.objects.get(id=shepherd_username)
        else:
            chief_shep_bypass = False

        context['shepherd'] = shepherd

        if user.level == 'core_shep' or chief_shep_bypass:
            sheep_reports = ShepherdReport.shepherd_manager.retrieve_sheep_details_who_submit_reports(shepherd=shepherd)
            context['sheep_reports'] = sheep_reports
            context['chief_shep_bypass'] = chief_shep_bypass

            diligent_sheep, full_names = ShepherdReport.shepherd_manager.most_diligent_sheep(shepherd=shepherd)
            top_books = ShepherdReport.shepherd_manager.most_read_books(shepherd=shepherd)
            unique_gender, gender_percentage = ShepherdReport.shepherd_manager.overall_gender_percentage(
                shepherd=shepherd)

            pass
        elif user.level == 'chief_shep':
            sheep_report_analysis = ShepherdReport.shepherd_manager.retrieve_sheep_reports_statistics()
            context['sheep_report_analysis'] = sheep_report_analysis

            diligent_sheep, full_names = ShepherdReport.shepherd_manager.most_diligent_sheep()
            top_books = ShepherdReport.shepherd_manager.most_read_books()
            unique_gender, gender_percentage = ShepherdReport.shepherd_manager.overall_gender_percentage()

        # Actions common to both chief_shepherd and core_shepherd

        if not isinstance(diligent_sheep, list) and diligent_sheep.any():
            context['top_5_diligent_sheep'] = list(diligent_sheep.index)
            context['top_5_diligent_sheep_counts'] = list(diligent_sheep.values)
            context['top_5_diligent_sheep_full_names'] = full_names
        else:
            context['top_5_diligent_sheep'] = None

        if not isinstance(top_books, list) and top_books.any():
            context['most_read_books'] = list(top_books.index)
            context['most_read_books_counts'] = list(top_books.values)
        else:
            context['most_read_books'] = None

        if unique_gender:
            context['unique_gender'] = unique_gender
            context['gender_percentage'] = gender_percentage
        else:
            context['unique_gender'] = None

        context['shepherd'] = shepherd

        return context


class SearchInterfaceView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/search_interface.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep' or self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = title
        context['category'] = 'Search'

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        context['users'] = CustomUser.objects.all()
        context['skills'] = Skill.objects.all()
        context['courses'] = Course.objects.all()

        context['gender_filter'] = 'All'
        context['graduate_status_filter'] = 'All'
        context['employment_status_filter'] = 'All'
        context['marital_status_filter'] = 'All'
        context['skill_filter'] = 'All'
        context['course_filter'] = 'All'

        user_columns = self.request.user.to_dict().keys()
        # user_columns = [" ".join(col.split("_")) for col in user_columns]
        context['user_columns'] = user_columns
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # Check if user want to download search instead
        is_download = request.GET.get('download', False)

        if is_download:
            gender = request.GET['gender_filter']
            graduate_status = request.GET['graduate_status_filter']
            employment_status = request.GET['employment_status_filter']
            marital_status = request.GET['marital_status_filter']
            skills = request.GET['skill_filter']
            course = request.GET['course_filter']
        else:
            gender = request.POST['search_filter_gender']
            graduate_status = request.POST['search_filter_graduate_status']
            employment_status = request.POST['search_filter_employment_status']
            marital_status = request.POST['search_filter_marital_status']
            skills = request.POST['search_filter_skills']
            course = request.POST['search_filter_course']

        search_result = CustomUser.objects.all()
 
        if gender != 'All':
            search_result = search_result.filter(gender=gender)
        if graduate_status != 'All':
            search_result = search_result.filter(graduate_status=graduate_status if graduate_status else None)
        if employment_status != 'All':
            search_result = search_result.filter(employment_status=employment_status)
        if marital_status != 'All':
            search_result = search_result.filter(marital_status=marital_status)
        if skills != 'All':
            search_result = search_result.filter(skills__icontains=skills)
        if course != 'All':
            search_result = search_result.filter(course_of_study=course)

        if is_download:
            fields = list(request.POST.keys())
            fields.remove('csrfmiddlewaretoken')

            # if the list is empty, still download everything
            if len(fields) == 0:
                fields = [
                    'first_name', 'last_name', 'username', 'gender', 'date_of_birth',
                    'about', 'phone_number', 'email', 'occupation', 'address', 'skills',
                    'blood_group', 'genotype', 'chronic_illness', 'lga', 'state', 'country',
                    'course_of_study', 'years_of_study', 'current_year_of_study', 'final_year_status',
                    'next_of_kin_full_name', 'next_of_kin_relationship', 'next_of_kin_phone_number',
                    'next_of_kin_address', 'gift_graces', 'callings', 'reveal_calling_by_shepherd',
                    'unit_of_work', 'shepherd', 'sub_shepherd', 'last_active_date', 'shoe_size',
                    'cloth_size', 'level'
                ]
            data = search_result.values(*fields)
            response = convert_to_format(data, f"Profiles {datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}", 'excel')
            return response

        context['gender_filter'] = gender
        context['graduate_status_filter'] = graduate_status
        context['employment_status_filter'] = employment_status
        context['marital_status_filter'] = marital_status
        context['skill_filter'] = skills
        context['course_filter'] = course

        if search_result:
            context['status'] = True
            context['search_result'] = search_result
        else:
            context['status'] = False
        return render(request, 'pastoring/partial_html/search_result.html', context)


# #####################################  WORKSPACE SECTION  ##############################################
class CatalogView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/workspace/catalog/catalog.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Catalog'
        context['title'] = title
        context['user'] = self.request.user

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        context['total_catalog'] = Catalog.catalog_manager.total_number_of_catalog()
        context['no_of_faulty_catalog'], context['breakdown'] = Catalog.catalog_manager.retrieve_faulty_catalog()

        # retrieve only the catalog that has the correct date formatting
        catalogs = Catalog.objects.order_by('-correct_date')
        catalogs = [catalog for catalog in catalogs if catalog.correct_date]
        context['properly_formatted_catalogs'] = catalogs

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        catalog_pk = request.POST['pk']
        catalog_title = request.POST['catalog_title']

        catalog_date = request.POST['catalog_date']
        catalog_date = datetime.fromisoformat(catalog_date)

        catalog_recommended_book_movies = request.POST['catalog_recommended_book_movies']
        catalog_new_songs_received = request.POST['catalog_new_songs_received']
        catalog_testimonies = request.POST['catalog_testimonies']
        catalog_things_spoken_about = request.POST['catalog_things_spoken_about']
        catalog_meta_information = request.POST['catalog_meta_information']

        catalog = Catalog.objects.get(id=catalog_pk)
        catalog.sermon_title = catalog_title
        catalog.correct_date = catalog_date
        catalog.recommended_books_movies = catalog_recommended_book_movies
        catalog.new_songs_received = catalog_new_songs_received
        catalog.testimonies = catalog_testimonies
        catalog.things_spoken_about = catalog_things_spoken_about
        catalog.meta_information = catalog_meta_information

        catalog.save()

        return HttpResponseRedirect(reverse_lazy('pastoring:catalog'))


class AddCatalogView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/workspace/catalog/add_catalog.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Catalog'
        context['title'] = title
        context['user'] = self.request.user

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        date = request.POST['add_catalog_date']
        date = datetime.fromisoformat(date)

        title = request.POST['add_catalog_title']
        recommended_books_movies = request.POST['add_catalog_recommended_books_movies']
        new_song_received = request.POST['add_catalog_new_song_received']
        testimonies = request.POST['add_catalog_testimonies']
        things_spoken_about = request.POST['add_catalog_things_spoken_about']
        meta_information = request.POST['add_catalog_meta_information']

        catalog = Catalog(
            day=date.day, correct_date=date,
            sermon_title=title,
            things_spoken_about=things_spoken_about,
            testimonies=testimonies,
            new_songs_received=new_song_received,
            recommended_books_movies=recommended_books_movies,
            meta_information=meta_information
        )
        catalog.save()

        return self.render_to_response(context)


class FaultyCatalogView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/workspace/catalog/faulty_catalog.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):

            if 'action' in kwargs:
                action = kwargs['action']
                catalog_id = kwargs['pk']

                if action == 'delete':
                    Catalog.objects.get(id=catalog_id).delete()
                    return JsonResponse({})

            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Catalog'
        context['title'] = title
        context['user'] = self.request.user

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        context['no_of_faulty_catalog'], context['breakdown'], context[
            'faulty_catalog'] = Catalog.catalog_manager.retrieve_faulty_catalog(accept_catalog=True)

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if 'action' in kwargs:
            action = kwargs['action']
            catalog_id = kwargs['pk']

            if action == 'fix':
                date = request.POST['date']
                date = datetime.strptime(date, '%m/%d/%Y')

                sermon_title = request.POST['sermon_title']
                recommended_books_movies = request.POST['recommended_books_movies']
                new_songs_received = request.POST['new_songs_received']
                testimonies = request.POST['testimonies']
                things_spoken_about = request.POST['things_spoken_about']

                catalog = Catalog.objects.get(id=catalog_id)

                catalog.date = date
                catalog.sermon_title = sermon_title
                catalog.recommended_books_movies = recommended_books_movies
                catalog.new_songs_received = new_songs_received
                catalog.testimonies = testimonies
                catalog.things_spoken_about = things_spoken_about
                catalog.save()
        return HttpResponseRedirect(reverse_lazy('pastoring:faulty-catalog'))


class TestimoniesView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/workspace/testimonies/testimonies.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)

        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Testimonies'
        context['title'] = title
        context['user'] = self.request.user

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        context['testimonies'] = Testimony.objects.all()
        context['total_testimonies'] = len(context['testimonies'])

        context['unique_testifiers'] = np.unique(Testimony.objects.retrieve_unique_testifiers())
        context['no_of_testifiers'] = len(context['unique_testifiers'])

        return context

    def post(self, request, *args, **kwargs):
        pk = request.POST['pk']
        testifier = request.POST['testimony_testifier']
        date = request.POST['testimony_date']
        category = request.POST['testimony_category']
        message = request.POST['testimony_message']
        title = request.POST['testimony_title']

        testimony = Testimony.objects.get(id=int(pk))
        testimony.testifier = testifier
        testimony.date = date
        testimony.category = category
        testimony.message = message
        testimony.title = title
        testimony.save()

        return HttpResponseRedirect(reverse_lazy('pastoring:testimonies'))


class AddTestimonyView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/workspace/testimonies/add_testimonies.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['category'] = 'Testimonies'
        context['title'] = title
        context['user'] = self.request.user

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        date = request.POST['add_testimony_date']
        title = request.POST['add_testimony_title']
        testifier = request.POST['add_testimony_testifier']
        category = request.POST['add_testimony_category']
        message = request.POST['add_testimony_message']

        testimony = Testimony(testifier=testifier, title=title,
                              date=date, category=category,
                              message=message)
        testimony.save()

        context['upload_saved'] = True
        context['upload_title'] = title
        return self.render_to_response(context)


class PropheticWordsView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/workspace/prophetic_words/prophetic_words.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)

        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Prophetic Words'
        context['title'] = title
        context['user'] = self.request.user

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        context['prophetic_words'] = PropheticWord.objects.all()
        context['total_prophetic_words'] = len(context['prophetic_words'])

        context['unique_speakers'] = np.unique(PropheticWord.objects.retrieve_unique_speakers())
        context['no_of_speakers'] = len(context['unique_speakers'])

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        pk = request.POST['pk']
        title = request.POST['prophetic_word_title']
        date = request.POST['prophetic_word_date']
        speaker = request.POST['prophetic_word_speaker']
        category = request.POST['prophetic_word_category']
        message = request.POST['prophetic_word_message']
        ai_generated_summary = request.POST['prophetic_ai_generated_summary']
        ai_generated_keywords = request.POST['prophetic_ai_generated_keyword']

        prophetic_word = PropheticWord.objects.get(id=int(pk))
        prophetic_word.title = title
        prophetic_word.date = date
        prophetic_word.speaker = speaker
        prophetic_word.category = category
        prophetic_word.message = message
        prophetic_word.ai_generated_summary = ai_generated_summary
        prophetic_word.ai_generated_keywords = ai_generated_keywords
        prophetic_word.save()

        return HttpResponseRedirect(reverse_lazy('pastoring:prophetic_words'))


class AddPropheticWordsView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/workspace/prophetic_words/add_prophetic_words.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['category'] = 'Prophetic Words'
        context['title'] = title
        context['user'] = self.request.user

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        title = request.POST['add_prophetic_word_title']
        date = request.POST['add_prophetic_word_date']
        speaker = request.POST['add_prophetic_word_speaker']
        category = request.POST['add_prophetic_word_category']
        message = request.POST['add_prophetic_word_message']

        prophetic_word = PropheticWord(title=title, date=date, speaker=speaker,
                                       category=category, message=message)
        prophetic_word.save()

        context['upload_saved'] = True
        context['upload_title'] = title
        return self.render_to_response(context)


class BlogView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/workspace/blog/blog.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):

            if 'unique_id' in self.request.GET:
                unique_id = self.request.GET.get('unique_id')

                blog = Blog.objects.get(id=unique_id)
                context = {
                    'title': blog.title, 'date': blog.date,
                    'message': blog.message, 'author': blog.author
                }
                return JsonResponse(context, safe=False)

            return super().get(request, *args, **kwargs)

        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Blog'
        context['title'] = title
        context['user'] = self.request.user

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        context['blog'] = Blog.objects.all()
        context['total_blog'] = len(context['blog'])

        return context

    def post(self, request, *args, **kwargs):
        pk = request.POST['pk']
        title = request.POST['blog_title']
        author = request.POST['blog_author']
        date = request.POST['blog_date']
        message = request.POST['blog_message']

        blog = Blog.objects.get(id=int(pk))
        blog.title = title
        blog.author = author
        blog.date = date
        blog.message = message
        blog.save()

        return HttpResponseRedirect(reverse_lazy('pastoring:blog'))


class AddBlogView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/workspace/blog/add_blog.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['category'] = 'Blog'
        context['title'] = title
        context['user'] = self.request.user

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        title = request.POST['add_blog_title']
        author = request.POST['add_blog_author']
        date = request.POST['add_blog_date']
        message = request.POST['add_blog_message']

        blog = Blog(title=title, author=author, date=date, message=message)
        blog.save()

        context['upload_saved'] = True
        context['upload_title'] = title
        return self.render_to_response(context)


class SermonsView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/workspace/sermons/sermons.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)

        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Sermons'
        context['title'] = title
        context['user'] = self.request.user

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        context['sermons'] = Sermon.objects.all()
        context['total_sermons'] = len(context['sermons'])

        context['unique_series_title'] = np.unique(Sermon.objects.retrieve_unique_sermon_series())
        context['no_of_series_title'] = len(context['unique_series_title'])

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        pk = request.POST['pk']
        title = request.POST['sermon_title']
        series_title = request.POST['sermon_series_title']
        date = request.POST['sermon_date']
        category = request.POST['sermon_category']
        download_link = request.POST['sermon_download_link']

        sermon = Sermon.objects.get(id=int(pk))
        sermon.title = title
        sermon.series_title = series_title
        sermon.date = date
        sermon.category = category
        sermon.download_link = download_link
        sermon.save()

        return HttpResponseRedirect(reverse_lazy('pastoring:sermons'))


class AddSermonsView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/workspace/sermons/add_sermons.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['category'] = 'Sermons'
        context['title'] = title
        context['user'] = self.request.user

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        title = request.POST['add_sermon_title']
        series_title = request.POST['add_sermon_series_title']
        date = request.POST['add_sermon_date']
        category = request.POST['add_sermon_category']
        download_link = request.POST['add_sermon_download_link']

        sermon = Sermon(title=title, series_title=series_title, date=date,
                        category=category, download_link=download_link)
        sermon.save()

        context['upload_saved'] = True
        context['upload_title'] = title
        return self.render_to_response(context)


class GeneratedNewsView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/workspace/prophetic_words/generated_news.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden("You are not a Shepherd...please go back")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['developers'] = developers
        context['user'] = self.request.user
        context['title'] = title

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        if 'keywords' in self.request.GET:
            keywords = self.request.GET['keywords'].strip().split(',')

            context['keywords'] = keywords
        return context

    def post(self, request, *args, **kwargs):
        keyword = request.POST['keyword'].strip()

        random_list = [10, 3, 34, 11, 1, 15, 40]

        # response = requests.get(url, headers=headers, params=querystring)

        # print(response.json())

        # query Google News API
        google_api_url = f"https://gnews.io/api/v4/search?q={keyword}&lang=en&max=10&apikey="

        querystring = {
            "q": keyword,
            "lang": 'en',
            "max": 10,
            "apikey": "cb52b85cb4f1f7fafd116445f37be30d"
        }
        gnews_response = requests.get(google_api_url, params=querystring)
        gnews_response = gnews_response.json()

        html_markup = ""

        if gnews_response:
            for article in gnews_response['articles']:
                html_markup += f"""
                <div class="col-lg-4 col-md-6">
                    <div class="card p-3">
                        <img class="img-fluid" src="{article['image']}">
                        <div class="card-body">
                        <h5 class="card-title">{article['title']}</h5>
                        <p class="card-text">{article.get('description', '')}</p>
                        <a href="{article['url']}" target="_blank" class="btn btn-primary">See Full news</a>
                        </div>
                    </div>
                </div>
                """

        url = "https://news-api14.p.rapidapi.com/search"

        querystring = {"q": keyword, "language": "en", "pageSize": "10"}

        headers = {
            "X-RapidAPI-Key": "9c62ae64a0msh792c6aa55345b04p1fac91jsna0d4633ec694",
            "X-RapidAPI-Host": "news-api14.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        news_api_response = response.json()

        if news_api_response:
            for article in news_api_response['articles']:
                html_markup += f"""
                <div class="col-lg-4 col-md-6">
                    <div class="card p-3">
                        <img class="img-fluid" src="{article.get('thumbnail', '')}">
                        <div class="card-body">
                        <h5 class="card-title">{article.get('title', '')}</h5>
                        <p class="card-text">{article.get('publisher', '').get('name', '')}</p>
                        <a href="{article.get('url', '')}" target="_blank" class="btn btn-primary">See Full news</a>
                        </div>
                    </div>
                </div>

                """

        url = "https://google-news13.p.rapidapi.com/search"

        querystring = {"keyword": keyword, "lr": "en-US"}

        headers = {
            "X-RapidAPI-Key": "9c62ae64a0msh792c6aa55345b04p1fac91jsna0d4633ec694",
            "X-RapidAPI-Host": "google-news13.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        rapid_response = response.json()

        for article in rapid_response['items']:
            # image = article['images']['thumbnail']
            html_markup += f"""
            <div class="col-lg-4 col-md-6">
                <div class="card p-3">
                    <img class="img-fluid" src="{article['images'].get('thumbnail', '')}">
                    <div class="card-body">
                    <h5 class="card-title">{article.get('title', ''), ''}</h5>
                    <p class="card-text">{ article.get('snippet', '') }</p>
                    <a href="{article.get('newsUrl', '')}" target="_blank" class="btn btn-primary">See Full news</a>
                    </div>
                </div>
            </div>

            """

        context = {
            'confirm': True,
            'articles': html_markup
        }

        return JsonResponse(context)


class ShortenedUrlsView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/workspace/url_shortener/url_shortener.html'

    def get(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'permission'):
            Permission.objects.create(name=self.request.user)
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep' or self.request.user.permission.short_link_manager):
            
            """Ensures that only core shepherd, chief shep and those who have specific permission
            have access to this page"""
            if 'api' in request.GET:  # READ API
                shortened_urls = UrlShortener.objects.filter(user=self.request.user)
                shortened_urls = {'urls': [url.to_json() for url in shortened_urls]}

                return JsonResponse(shortened_urls, safe=False)
            elif 'delete' in request.GET:  # DELETE API
                url = request.GET['delete']

                try:
                    url = UrlShortener.objects.get(original_url=url)
                    url.delete()
                    return JsonResponse({'confirmation': True})
                except Exception as e:
                    response = {
                        'confirmation': False,
                        'error_message': str(e)
                    }
                    return JsonResponse(response, safe=False)  
            return super().get(request, *args, **kwargs)

        return HttpResponseForbidden('You are not a Shepherd...please go back')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.permission.short_link_manager and (
            self.request.user.level == 'core_shep' or 
                self.request.user.level == 'chief_shep'):
            
            context['restricted_access'] = False
        else:
            context['restricted_access'] = True
            

        context['category'] = 'Shortened Url'
        context['developers'] = developers
        context['title'] = title
        context['user'] = self.request.user

        # Get all the active notification for the user
        pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                             is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(pastoral_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        # Get all the url shortened by this user
        shortened_urls = UrlShortener.objects.filter(user=self.request.user)
        context['shortened_urls'] = shortened_urls

        # if submission of url is successful
        submission = self.request.GET.get('submission', None)
        if submission == 'false':
            context['error_message'] = self.request.GET.get('error_message')

        context['submission'] = submission

        return context

    def post(self, request, *args, **kwargs):

        if 'edit' in request.GET:
            method = 'update'
        else:
            method = request.POST['method']

        if method == 'add':  # ADD API
            original_url = request.POST['addOriginalUrl']
            short_url = request.POST['addShortUrl']

            try:
                url = UrlShortener.objects.create(
                    original_url=original_url,
                    shortened_url=short_url,
                    user=request.user
                )
            except IntegrityError as e:
                return HttpResponseRedirect(f"{reverse_lazy('pastoring:shorten_url')}?submission=false&error_message={e}")
            
            return HttpResponseRedirect(f"{reverse_lazy('pastoring:shorten_url')}?submission=true")

        elif method == 'update':  # UPDATE API
            url_id = request.POST['url_id']
            original_url = request.POST['original_url']
            short_url = request.POST['short_url']

            try:
                url = UrlShortener.objects.get(id=url_id)
                url.original_url = original_url
                url.shortened_url = short_url

                url.save()
            except Exception as e:
                return JsonResponse({'confirm': False, 'error_message': str(e)})
            
            return JsonResponse({'confirm': True})




#########################  END WORKSPACE  ##########################


class FetchView(LoginRequiredMixin, View):
    """Use to pseudo api for retrieving value from the database, according
    to the specification

    TODO: Move it to the API section
    """
    login_url = reverse_lazy('users-login')

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and self.request.user.level == 'chief_shep':
            field = kwargs['field']
            value = kwargs['value']

            item_list = get_user_model().objects.get_particular_field_value_only(field, value)
            return JsonResponse(item_list, safe=False)

        return HttpResponseForbidden("You are not a Chief Shepherd...please go back")
