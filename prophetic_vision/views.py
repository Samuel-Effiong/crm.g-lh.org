from datetime import datetime, time

from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, JsonResponse

from .models import PropheticVision
from home.models import RecentActivity, Notification


title = "GLH-FAM"


class PropheticVisionListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/table/table-data.html'
    context_object_name = 'lists'

    def get_queryset(self):
        username = get_object_or_404(get_user_model(), username=self.request.user.username)
        return PropheticVision.objects.filter(username=username).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Prophetic Vision'
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
        description = request.POST['prophetic_vision_description']
        date = request.POST['prophetic_vision_date']
        body = request.POST['prophetic_vision_body']

        prophetic_vision = PropheticVision(description=description, body=body,
                                           date=datetime.strptime(date, '%m/%d/%Y'),
                                           username=request.user)
        prophetic_vision.save()

        recent = RecentActivity(username=request.user, category="prophetic_vision",
                                details=f"Prophetic on {str(date)}")

        recent.save()

        return HttpResponseRedirect(reverse_lazy('prophetic_vision:list'))


class PropheticVisionDetailView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('users-login')
    template_name = "dashboard/special-pages/detail.html"
    context_object_name = 'detail'
    model = PropheticVision

    def get_context_data(self, **kwargs):
        context = super(PropheticVisionDetailView, self).get_context_data(**kwargs)

        context['category'] = 'Prophetic Vision'
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
        context = {'category': 'Prophetic Vision', 'user': self.request.user, 'title': title}

        try:
            description = request.POST['description']
            date = request.POST['date']
            body = request.POST['body']

            prophetic_vision = PropheticVision.objects.get(id=kwargs['pk'])
            prophetic_vision.description = description
            prophetic_vision.body = body
            prophetic_vision.date = datetime.strptime(date, '%m/%d/%Y')

            prophetic_vision.save()
        except Exception:
            context['detail_update'] = 'failed'
            return self.render_to_response(context)

        recent = RecentActivity(username=request.user, category="prophetic_vision",
                                details=f'Prophetic on {date}')
        recent.save()

        context['detail'] = PropheticVision.objects.get(id=kwargs['pk'])
        context['detail_update'] = 'successful'

        if request.htmx:
            return render(request, 'dashboard/special-pages/partial_html/detail.html', context)
        return self.render_to_response(context)
