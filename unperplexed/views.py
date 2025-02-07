from django.shortcuts import render

from django.urls import reverse_lazy
from django.views.generic.base import TemplateView

from django.http import (
    HttpResponseRedirect, JsonResponse, HttpResponseForbidden,
    HttpResponse
)

from users.my_models import CustomUser

from . import models


title = "Unperplexed Consulting"
subtitle = 'Unperplexed'

# Create your views here.

class Homepage(TemplateView):
    template_name = "unperplexed/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['title'] = title
        context['subtitle'] = subtitle
        
        
        return context
    
    
class DashboardView(TemplateView):
    template_name = 'unperplexed/admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['title'] = title
        context['project_title'] = subtitle
        
        context['category'] = 'Dashboard'
        context['page'] = 'Unperplexed'
        context['user'] = user
        
        return context
    

class WorkerView(TemplateView):
    template_name = 'unperplexed/admin/worker.html'
    
    def get(self, request, *args, **kwargs):
        
        if request.htmx:
            if 'delete' in request.GET:
                worker_id = request.GET['delete']
                models.Worker.objects.get(id=worker_id).delete()
                
            if 'edit_worker' in request.GET:
                worker_id = request.GET['edit_worker']
                
                worker = models.Worker.objects.get(id=worker_id)
                return render(request, 'unperplexed/admin/partials/edit_worker_partial.html', {'worker': worker})
            
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['title'] = title
        context['project_title'] = subtitle
        
        context['category'] = 'Worker'
        context['page'] = 'Unperplexed'
        context['user'] = user
        
        # retrieve a list of users who have filled in thier skills
        users_with_skills = CustomUser.objects.exclude(skills__isnull=True).exclude(skills__exact="")
        context['user_with_skills'] = users_with_skills
        context['workers'] = models.Worker.objects.all
        
        return context
    
    def post(self, request, **kwargs):
        
        if 'edit_worker' in request.GET:
            worker_id = request.GET['edit_worker']
            category = request.POST['category']
            rating = request.POST['rating']
            availability_status = True if request.POST['availability_status'] == 'yes' else False
            
            worker = models.Worker.objects.get(id=worker_id)
            worker.category = category
            worker.rating = rating
            worker.availability_status = availability_status
            
        else: 
            
            name = request.POST['name']
            name = CustomUser.objects.get(username=name)
            
            category = request.POST['category']
            rating = request.POST['rating']
            availability_status = True if request.POST['availability_status'].lower().strip() == 'yes' else False
            
            worker = models.Worker(
                name=name, category=category,
                rating=rating, availability_status=availability_status
            )
            
        worker.save()
        return HttpResponseRedirect(reverse_lazy('unperplexed:worker'))
    
    
class WorkerDetail(TemplateView):
    template_name = 'unperplexed/admin/worker_detail.html'
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def post(self, **kwargs):
        pass
    
class ContractView(TemplateView):
    template_name = 'unperplexed/admin/contract.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context[""] = 'love' 
        return context 
    

class OrganizationView(TemplateView):
    template_name = 'unperplexed/organization.html'
    
    
    