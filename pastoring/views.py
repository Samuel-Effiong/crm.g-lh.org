from typing import Any, Dict

import os
import numpy as np
import pandas as pd
from datetime import datetime


from django import http
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.http import HttpRequest, HttpResponse

from django.views.generic.base import TemplateView, View

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from users.models import Shepherd, SubShepherd, CustomUser, Catalog
from users.my_models.users import LEVEL_CHOICES

from church_work.models import ChurchWork
from evangelism.models import Evangelism
from personal_development.models import BibleReading, PrayerMarathon, ShepherdReport
from prophetic_vision.models import PropheticVision

from home.models import Notification

from .models import (Testimony, PropheticWord, Blog, Sermon)


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


class SheepSummaryDetailView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'pastoring/sheep_summary_details.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
                self.request.user.level == 'core_shep'
                or self.request.user.level == 'chief_shep'):
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
            shepherd = Shepherd.objects.get(name__username=shepherd_username)
        else:
            chief_shep_bypass = False

        context['shepherd'] = shepherd

        if user.level == 'core_shep' or chief_shep_bypass:
            sheep_reports = ShepherdReport.shepherd_manager.retrieve_sheep_details_who_submit_reports(shepherd=shepherd)
            context['sheep_reports'] = sheep_reports
            context['chief_shep_bypass'] = chief_shep_bypass

            diligent_sheep, full_names = ShepherdReport.shepherd_manager.most_diligent_sheep(shepherd=shepherd)
            top_books = ShepherdReport.shepherd_manager.most_read_books(shepherd=shepherd)
            unique_gender, gender_percentage = ShepherdReport.shepherd_manager.overall_gender_percentage(shepherd=shepherd)

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

        context['no_of_faulty_catalog'], context['breakdown'], context['faulty_catalog'] = Catalog.catalog_manager.retrieve_faulty_catalog(accept_catalog=True)

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
        ai_generated_kewywords = request.POST['prophetic_ai_generated_keywords']

        prophetic_word = PropheticWord.objects.get(id=int(pk))
        prophetic_word.title = title
        prophetic_word.date = date
        prophetic_word.speaker = speaker
        prophetic_word.category = category
        prophetic_word.message = message
        prophetic_word.ai_generated_keywords = ai_generated_kewywords
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
