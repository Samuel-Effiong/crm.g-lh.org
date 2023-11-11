
from datetime import datetime, time

from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy, resolve
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import get_user_model

from .models import Evangelism
from home.models import RecentActivity, Notification

title = 'GLH-FAM'


class EvangelismListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/table/table-data.html'
    context_object_name = 'lists'

    def get_queryset(self):
        username = get_object_or_404(get_user_model(), username=self.request.user.username)
        return Evangelism.objects.filter(username=username).order_by('-no_led_to_christ')

    def get_context_data(self, **kwargs):
        context = super(EvangelismListView, self).get_context_data(**kwargs)

        context['category'] = 'Evangelism'
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
        field_of_visit = request.POST['evangelism_field_of_visit']
        hours_spent = request.POST['evangelism_hours_spent']
        led_to_christ = request.POST['evangelism_no_led_to_christ']
        follow_up = request.POST['evangelism_follow_up']
        invites = request.POST['evangelism_no_of_invites']
        baptism = request.POST['evangelism_no_baptism']
        people_prayed = request.POST['evangelism_people_prayed']
        prints_shared = request.POST['evangelism_prints_shared']
        snippets = request.POST['evangelism_snippets']
        messages_shared = request.POST['evangelism_message_shared']
        first_date = request.POST['evangelism_first_date']
        last_date = request.POST['evangelism_last_date']

        evangelism = Evangelism(field_of_visit=field_of_visit, hours_spent_per_week=hours_spent,
                                no_led_to_christ=led_to_christ, follow_up=follow_up,
                                invitees=invites, holy_spirit_baptism=baptism,
                                no_of_people_prayed=people_prayed, prints_shared=prints_shared,
                                snippets=snippets, messages=messages_shared,
                                first_date_of_week=datetime.strptime(first_date, '%m/%d/%Y'),
                                last_date_of_week=datetime.strptime(last_date, '%m/%d/%Y'),
                                username=request.user)

        evangelism.save()

        recent = RecentActivity(username=request.user, category="evangelism",
                                details="Evangelism")
        recent.save()

        return HttpResponseRedirect(reverse_lazy('evangelism:list'))


class EvangelismDetailView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/special-pages/detail.html'
    context_object_name = 'detail'
    model = Evangelism

    def get_context_data(self, **kwargs):
        context = super(EvangelismDetailView, self).get_context_data(**kwargs)

        context['category'] = 'Evangelism'
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

        context['category'] = 'Evangelism'
        context['user'] = self.request.user
        context['title'] = title

        try:
            field_of_visit = request.POST['field_of_visit']
            hours_spent = request.POST['hours_spent']
            led_to_christ = request.POST['no_led_to_christ']
            follow_up = request.POST['follow_up']
            invites = request.POST['no_of_invites']
            baptism = request.POST['no_of_baptism']
            people_prayed = request.POST['people_prayed']
            prints_shared = request.POST['prints_shared']
            messages_shared = request.POST['messages_shared']
            snippets = request.POST['snippets']
            first_date = request.POST['first_date']
            last_date = request.POST['last_date']

            evangelism = Evangelism.objects.get(id=kwargs['pk'], username=request.user)
            evangelism.field_of_visit = field_of_visit
            evangelism.hours_spent_per_week = hours_spent
            evangelism.no_led_to_christ = led_to_christ
            evangelism.follow_up = follow_up
            evangelism.invitees = invites
            evangelism.holy_spirit_baptism = baptism
            evangelism.no_of_people_prayed = people_prayed
            evangelism.prints_shared = prints_shared
            evangelism.snippets = snippets
            evangelism.messages = messages_shared
            evangelism.first_date_of_week = datetime.strptime(first_date, '%m/%d/%Y')
            evangelism.last_date_of_week = datetime.strptime(last_date, '%m/%d/%Y')

            evangelism.save()
        except Exception:
            context['detail_update'] = 'failed'
            return self.render_to_response(context)

        recent = RecentActivity(username=request.user, category="evangelism",
                                details='Updated Evangelism')
        recent.save()

        context['detail'] = Evangelism.objects.get(id=kwargs['pk'])
        context['detail_update'] = 'successful'
        return self.render_to_response(context)


class UpdateEvangelismDetailView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/special-pages/detail.html'

    def get_context_data(self, **kwargs):
        context = super(UpdateEvangelismDetailView, self).get_context_data(**kwargs)

        context['category'] = 'Evangelism'
        context['user'] = self.request.user
        context['title'] = title

        return context

    def post(self, request, **kwargs):
        field_of_visit = request.POST['field_of_visit']
        hours_spent = request.POST['hours_spent']
        led_to_christ = request.POST['no_led_to_christ']
        follow_up = request.POST['follow_up']
        invites = request.POST['invites']
        baptism = request.POST['baptism']
        people_prayed = request.POST['people_prayed']
        prints_shared = request.POST['prints_shared']
        messages_shared = request.POST['messages']
        snippets = request.POST['snippets']
        first_date = request.POST['first_date']
        last_date = request.POST['last_date']

        evangelism = Evangelism.objects.get(id=kwargs['pk'], username=request.user)
        evangelism.field_of_visit = field_of_visit
        evangelism.hours_spent_per_week = hours_spent
        evangelism.no_led_to_christ = led_to_christ
        evangelism.follow_up = follow_up
        evangelism.invitees = invites
        evangelism.holy_spirit_baptism = baptism
        evangelism.no_of_people_prayed = people_prayed
        evangelism.prints_shared = prints_shared
        evangelism.snippets = snippets
        evangelism.messages = messages_shared
        evangelism.first_date_of_week = datetime.strptime(first_date, '%m/%d/%Y')
        evangelism.last_date_of_week = datetime.strptime(last_date, '%m/%d/%Y')

        evangelism.save()

        recent = RecentActivity(username=request.user, category="evangelism",
                                details='Updated Evangelism')
        recent.save()

        return JsonResponse({'love': 'You'})
