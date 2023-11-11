from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth import get_user_model

from datetime import datetime

datetime.now()


developers = "God's Lighthouse Developers Team (GDevT)"
title = 'GLH-FAM'


# Create your views here.
class Dashboard(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'hod_report/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Dashboard'
        context['developers'] = developers
        context['user'] = self.request.user
        context['title'] = title

        context['day_period'] = datetime.now().strftime('%p')

        return context


