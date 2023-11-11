from datetime import datetime, time
from typing import Any, Dict
from django.db.models.query import QuerySet

from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import get_user_model

from .models import BibleReading, PrayerMarathon, ShepherdReport
from home.models import RecentActivity, Notification

# Create your views here.

title = 'GLH-FAM'


class BibleReadingListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/table/table-data.html'
    context_object_name = 'lists'

    def get_queryset(self):
        username = get_object_or_404(get_user_model(), username=self.request.user.username)
        return BibleReading.objects.filter(username=username).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['bible_challenge_on'] = True
        context['category'] = 'Bible Reading'
        context['user'] = self.request.user
        context['title'] = title

        # Get all the active notification for the user
        general_notifications = Notification.objects.filter(target=self.request.user, exposure_level='general',
                                                            is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(general_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        return context

    def post(self, request, **kwargs):

        try:
            bible_passage = request.POST['bible_passage']
        except:
            bible_passage = request.POST['custom_bible_passage']

        comment = request.POST['bible_reading_comment']
        date = request.POST['bible_reading_date']
        status = request.POST['bible_reading_status']

        bible_reading = BibleReading(bible_passage=bible_passage, comment=comment,
                                     date=datetime.strptime(date, '%m/%d/%Y'), status=status,
                                     username=request.user)
        bible_reading.save()

        recent = RecentActivity(username=request.user, category="bible_reading",
                                details=f"Read {bible_passage}")
        recent.save()

        return HttpResponseRedirect(reverse_lazy('bible_reading:list'))


class BibleReadingDetailView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/special-pages/detail.html'
    context_object_name = 'detail'
    model = BibleReading

    def get_context_data(self, **kwargs):
        context = super(BibleReadingDetailView, self).get_context_data(**kwargs)

        context['category'] = 'Bible Reading'
        context['user'] = self.request.user
        context['title'] = title

        # Get all the active notification for the user
        general_notifications = Notification.objects.filter(target=self.request.user, exposure_level='general',
                                                            is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(general_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        return context

    def post(self, request, **kwargs):
        context = {'category': 'Bible Reading', 'user': self.request.user, 'title': title}

        try:
            comment = request.POST['comment']
            date = request.POST['date']
            status = request.POST['status']

            bible_reading = BibleReading.objects.get(id=kwargs['pk'], bible_passage=kwargs['passage'],
                                                     username=request.user)

            bible_reading.comment = comment
            bible_reading.status = status
            bible_reading.date = datetime.strptime(date, '%m/%d/%Y')

            bible_reading.save()
        except Exception:
            context['detail_update'] = 'failed'
            return self.render_to_response(context)

        recent = RecentActivity(username=request.user, category="bible_reading",
                                details=f"Updated {kwargs['passage']}")
        recent.save()

        context['detail'] = BibleReading.objects.get(id=kwargs['pk'])
        context['detail_update'] = 'successful'
        return self.render_to_response(context)


class PrayerMarathonListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/table/table-data.html'
    context_object_name = 'lists'

    def get_queryset(self):
        username = get_object_or_404(get_user_model(), username=self.request.user.username)
        return PrayerMarathon.objects.filter(username=username).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Prayer Marathon'
        context['user'] = self.request.user
        context['title'] = title

        # Get all the active notification for the user
        general_notifications = Notification.objects.filter(target=self.request.user, exposure_level='general',
                                                            is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(general_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        return context

    def post(self, request, **kwargs):
        comment = request.POST['prayer_marathon_comment']
        date = request.POST['prayer_marathon_date']

        prayer_marathon = PrayerMarathon(comment=comment,
                                         date=datetime.strptime(date, '%m/%d/%Y'),
                                         username=request.user)

        prayer_marathon.save()

        recent = RecentActivity(username=request.user, category="prayer_marathon",
                                details='Intercession')
        recent.save()

        return HttpResponseRedirect(reverse_lazy('prayer_marathon:list'))


class PrayerMarathonDetailView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/special-pages/detail.html'
    context_object_name = 'detail'
    model = PrayerMarathon

    def get_context_data(self, **kwargs):
        context = super(PrayerMarathonDetailView, self).get_context_data(**kwargs)

        context['category'] = 'Prayer Marathon'
        context['user'] = self.request.user
        context['title'] = title

        # Get all the active notification for the user
        general_notifications = Notification.objects.filter(target=self.request.user, exposure_level='general',
                                                            is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(general_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        return context

    def post(self, request, **kwargs):
        context = {}

        context['category'] = 'Prayer Marathon'
        context['user'] = self.request.user
        context['title'] = title

        try:
            comment = request.POST['comment']
            date = request.POST['date']

            prayer_marathon = PrayerMarathon.objects.get(id=kwargs['pk'], username=request.user)
            prayer_marathon.comment = comment
            prayer_marathon.date = datetime.strptime(date, '%m/%d/%Y')

            prayer_marathon.save()
        except IndexError:
            context['detail_update'] = 'failed'
            return self.render_to_response(context)

        # Save Recent Activity
        recent = RecentActivity(username=request.user, category="prayer_marathon",
                                details='Intercession')
        recent.save()

        context['detail'] = PrayerMarathon.objects.get(id=kwargs['pk'])
        context['detail_update'] = 'successful'
        return self.render_to_response(context)


class ShepherdReportListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/table/table-data.html'
    context_object_name = 'lists'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        if 'shepherd_bypass' in self.request.GET:
            self.template_name = 'pastoring/table-data.html'

    def get_queryset(self) -> QuerySet[Any]:
        username = self.request.user
        if 'shepherd_bypass' in self.request.GET:
            self.sheep_username = get_user_model().objects.get(username=self.request.GET['sheep_username'])
        else:
            self.sheep_username = self.request.user.username
        return ShepherdReport.objects.filter(sender=self.sheep_username).order_by('-date')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['category'] = 'Shepherd Report'
        context['title'] = title
        context['user'] = self.request.user

        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        if 'shepherd_bypass' in self.request.GET:
            context['sheep'] = self.sheep_username
            context['shepherd_bypass'] = True

            pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                                 is_activated=False)
            active_notifications = list(pastoral_notifications) + list(all_notifications)
        else:
            context['shepherd_bypass'] = False

            # Get all the active notification for the user
            general_notifications = Notification.objects.filter(target=self.request.user, exposure_level='general',
                                                                is_activated=False)

            active_notifications = list(general_notifications) + list(all_notifications)

        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        return context

    def post(self, request, **kwargs):
        date = request.POST['shepherd_report_date']
        church_work = request.POST['shepherd_report_church_work']
        personal_details = request.POST['shepherd_report_personal_details']
        books_read = request.POST['shepherd_report_books_read']

        shepherd_report = ShepherdReport(church_work=church_work, personal_details=personal_details,
                                         books_read=books_read, date=datetime.strptime(date, '%m/%d/%Y'),
                                         sender=request.user, receiver=request.user.shepherd)

        shepherd_report.save()

        user = request.user
        shepherd = user.shepherd

        if shepherd:
            notification = Notification(target=shepherd.name, mode='Shepherd Report',
                                        activator=user, time_sensitivity='None', exposure_level='pastoral',
                                        message=f"Report receive from {user.username}",
                                        additional_info=f"{{'pk': {shepherd_report.pk}}}")
            notification.save()

        recent = RecentActivity(username=user, category='shepherd_report',
                                details=f'Written Report for Week {shepherd_report.date.isocalendar().week}')
        recent.save()

        return HttpResponseRedirect(reverse_lazy('shepherd_report:list'))


class ShepherdReportDetailView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/special-pages/detail.html'
    context_object_name = 'detail'
    model = ShepherdReport

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        if 'shepherd_bypass' in self.request.GET:
            self.template_name = 'pastoring/detail.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['category'] = 'Shepherd Report'
        context['user'] = self.request.user
        context['title'] = title

        # Get all the active notification for the user
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        if 'shepherd_bypass' in self.request.GET:
            context['shepherd_bypass'] = True

            pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                                 is_activated=False)
            active_notifications = list(pastoral_notifications) + list(all_notifications)
        else:
            context['shepherd_bypass'] = True

            general_notifications = Notification.objects.filter(target=self.request.user, exposure_level='general',
                                                                is_activated=False)
            active_notifications = list(general_notifications) + list(all_notifications)

        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        return context

    def post(self, request, **kwargs):
        context = {'category': 'Shepherd Report', 'user': self.request.user, 'title': title}

        # Get all the active notification for the user
        general_notifications = Notification.objects.filter(target=self.request.user, exposure_level='general',
                                                            is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)

        active_notifications = list(general_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        try:
            church_work = request.POST['church_work']
            personal_details = request.POST['personal_details']
            books_read = request.POST['books_read']

            shepherd_report = ShepherdReport.objects.get(id=kwargs['pk'], sender=request.user)

            shepherd_report.church_work = church_work
            shepherd_report.personal_details = personal_details
            shepherd_report.books_read = books_read

            shepherd_report.save()

            user = request.user
            shepherd = user.shepherd

            if shepherd:
                notification = Notification(target=shepherd.name, mode='Shepherd Report',
                                            activator=user, time_sensitivity='None', exposure_level='pastoral',
                                            message=f"{user.username} updated {'his' if user.gender == 'M' else 'her'} Week {shepherd_report.date.isocalendar().week} report")
                notification.save()

        except Exception as e:
            context['detail_update'] = 'failed'
            context['error_message'] = str(e)
            context['detail'] = ShepherdReport.objects.get(id=kwargs['pk'], username=request.user)
            return self.render_to_response(context)

        recent = RecentActivity(username=request.user, category='shepherd_report',
                                details=f"Updated Shepherd Report")
        recent.save()

        context['detail'] = ShepherdReport.objects.get(id=kwargs['pk'], username=request.user)
        context['detail_update'] = 'successful'
        return self.render_to_response(context)
