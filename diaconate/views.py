
import os, shutil
import pandas as pd
from datetime import datetime

from django.conf import settings
from django.urls import reverse_lazy
from django.shortcuts import render
from django.views.generic.base import TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from django.http import (HttpResponseRedirect, JsonResponse, 
                         HttpResponseForbidden, HttpResponse)

from .models import (
    TreasuryRequest, Asset, AssetCategory, AssetFile,
    STATUS_CHOICES, CONDITION_CHOICES, REQUEST_STATUS_CHOICES,
    LOCATION_CHOICES, SOURCE_OF_ITEM_CHOICES
)

from project_management.models import (
    DepartmentMember, 
    Diaconate, 
    Department,
    DepartmentProject,
    ProjectTarget
)


developers = "God's Lighthouse Developers Team (GDevT)"
title = 'GLH-FAM'
project_title = 'GLH-PROJ'


def is_member(user):
    """A utitlity function to check is a user belongs to any department"""
    member = DepartmentMember.objects.filter(member_name=user)
    return len(member) > 0



class TreasuryDashboardView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = "diaconate/treasury/dashboard.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
            self.request.user.level == 'core_shep' 
                or self.request.user == 'chief_shep'
                    or is_member(self.request.user)):
            
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden('You are not Authorized to come here...please Go back')

    def get_context_data(self, **kwargs) -> dict[str]:
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['category'] = 'Dashboard'
        context['page'] = 'Treasury'

        context['title'] = title
        context['user'] = user
        context['project_title'] = project_title

        # Context needed to handle the navigation menu

        department = DepartmentMember.objects.filter(member_name=user)
        
        if department:
            department = department.first().department_name


        if user.is_superuser:
            context['member_departments'] = Department.objects.all()
        else:
            context['member_departments'] = Department.objects.get_member_departments(user)
        context['department_leaders'] = [leader.member_name for leader in Department.objects.department_leaders() if leader]

        try:
            department_member = DepartmentMember.objects.get(member_name=user, department_name=department)
            context['department_membership'] = department_member
            context['is_department_leader'] = department.is_leader(department_member)
        except DepartmentMember.DoesNotExist:
            context['is_department_leader'] = False

        department_projects = DepartmentProject.objects.filter(department=department, status__in=['In Progress', 'Not Started'])
        context['department_projects'] = department_projects

        department_projects_status_statistic = DepartmentProject.objects.get_department_projects_status_statistic(department)
        context['department_project_status_statistic'] = department_projects_status_statistic

        all_department_pending_target = ProjectTarget.objects.all_department_pending_target(department)
        context['all_department_pending_target'] = all_department_pending_target

        # GET Member Activity in the project
        members, complete_project = department.member_activity_in_a_department()
        context['member_activity_in_a_department'] = zip(members, complete_project)

        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

        # end context for navigation menu



        # check if there is a treasury diaconate and adds a special link section
        # to access treasury related pages
        try:
            treasury = Diaconate.objects.get(name='TREASURY')
            membership = treasury.is_a_diaconate_member(user)

            if membership:
                context['treasury_membership'] = True
        except Diaconate.DoesNotExist as e:
            context['treasury_diaconate_unavailable'] = True
            
        percentage = 100
            
        context['assets'] = Asset.objects.all()
        context['treasury_requests'] = TreasuryRequest.objects.all()
        
        context['pending_requests'] = TreasuryRequest.objects.filter(status='Pending')

        context['approved_requests'] = TreasuryRequest.objects.filter(status='Approved')
        context['rejected_requests'] = TreasuryRequest.objects.filter(status='Rejected')
        
        assets_condition_excellent = Asset.objects.filter(condition='Excellent')
        assets_condition_good = Asset.objects.filter(condition='Good')
        assets_condition_bbiu = Asset.objects.filter(condition='Bad But In Use')
        assets_condition_bbcbf = Asset.objects.filter(condition='Bad But Can Be Fixed')
        assets_condition_bou = Asset.objects.filter(condition='Bad and Out of Use')
        asset_condition_vb = Asset.objects.filter(condition='Very Bad')
        
        context['assets_condition_excellent'] = assets_condition_excellent
        context['assets_condition_good'] = assets_condition_good
        context['assets_condition_bbiu'] = assets_condition_bbiu
        context['assets_condition_bbcbf'] = assets_condition_bbcbf
        context['assets_condition_bou'] = assets_condition_bou
        context['assets_condition_vb'] = asset_condition_vb
        
        

        return context


class TreasuryInventoryView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = "diaconate/treasury/inventory_list.html"
    
    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
            self.request.user.level == 'core_shep' 
                or self.request.user == 'chief_shep'
                    or is_member(self.request.user)):
            
            if request.htmx:
                context = {}
            
                if 'delete' in request.GET:
                    asset_id = request.GET['delete']
                    
                    asset = Asset.objects.get(id=asset_id)
                    context['confirm'] = False
                    context['error_message'] = f"{asset.name} successfully deleted"
                    asset.delete()
                    
                    context['treasury_assets'] = Asset.objects.all()
                    return render(request, 'diaconate/treasury/partial_html/inventory_list_partial.html', context)
                
                elif 'edit' in request.GET:
                    asset_id = request.GET['edit']
                    asset = Asset.objects.get(id=asset_id)
                    
                    context['asset'] = asset
                    context['asset_categories'] = AssetCategory.objects.all()
                    context['locations'] = [location[0] for location in LOCATION_CHOICES]
                    context['conditions'] = [condition[0] for condition in CONDITION_CHOICES]
                    context['source_of_items'] = [source[0] for source in SOURCE_OF_ITEM_CHOICES]
                    context['statuses'] = [status[0] for status in STATUS_CHOICES]
                
                    return render(request, 'diaconate/treasury/partial_html/edit_inventory_partial.html', context)
                elif 'delete_asset_file' in request.GET:
                    asset_id = request.GET['delete_asset_file']
                    asset_file = AssetFile.objects.get(id=asset_id)
                    asset = asset_file.asset_set.first()
                    
                    context['asset'] = asset
                    context['asset_categories'] = AssetCategory.objects.all()
                    context['locations'] = [location[0] for location in LOCATION_CHOICES]
                    context['conditions'] = [condition[0] for condition in CONDITION_CHOICES]
                    context['source_of_items'] = [source[0] for source in SOURCE_OF_ITEM_CHOICES]
                    context['statuses'] = [status[0] for status in STATUS_CHOICES]
                    
                    asset_file.delete()
                    
                    return render(request, 'diaconate/treasury/partial_html/edit_inventory_partial.html', context)
            else:         
                if 'download_inventory' in request.GET:
                    response = HttpResponse(
                        content_type="application/vnd.ms-excel",
                        charset="utf-8"
                    )
                    response['Content-Disposition'] = f'attachment; filename="Treasury Inventory.xlsx"'
                    
                    data = Asset.objects.values(
                        'id', 'name', 'description', 'category__name', 'purchase_date', 
                        'location', 'condition', 'source_of_item', 'status'
                    )
                    df = pd.DataFrame(data)
                    df.columns = [
                        'ID', "Name", "Description", "Category", "Purchase Date",
                        "Location", "Condition", "Source of Item", "Status"
                    ]
                    df.to_excel(response, "Treasury Inventory")
                    
                    return response
   
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden('You are not Authorized to come here...please Go back')

    def get_context_data(self, **kwargs) -> dict[str]:
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['category'] = 'Inventory'
        context['page'] = 'Treasury'

        context['title'] = title
        context['user'] = user
        context['project_title'] = project_title

        # Context needed to handle the navigation menu

        department = DepartmentMember.objects.filter(member_name=user)
        
        if department:
            department = department.first().department_name
            
        if user.is_superuser:
            context['member_departments'] = Department.objects.all()
        else:
            context['member_departments'] = Department.objects.get_member_departments(user)
        context['department_leaders'] = [leader.member_name for leader in Department.objects.department_leaders() if leader]

        try:
            department_member = DepartmentMember.objects.get(member_name=user, department_name=department)
            context['department_membership'] = department_member
            context['is_department_leader'] = department.is_leader(department_member)
        except DepartmentMember.DoesNotExist:
            context['is_department_leader'] = False

        department_projects = DepartmentProject.objects.filter(department=department, status__in=['In Progress', 'Not Started'])
        context['department_projects'] = department_projects

        department_projects_status_statistic = DepartmentProject.objects.get_department_projects_status_statistic(department)
        context['department_project_status_statistic'] = department_projects_status_statistic

        all_department_pending_target = ProjectTarget.objects.all_department_pending_target(department)
        context['all_department_pending_target'] = all_department_pending_target

        # GET Member Activity in the project
        members, complete_project = department.member_activity_in_a_department()
        context['member_activity_in_a_department'] = zip(members, complete_project)

        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

        # end context for navigation menu

        # check if there is a treasury diaconate and adds a special link section
        # to access treasury related pages
        try:
            treasury = Diaconate.objects.get(name='TREASURY')
            membership = treasury.is_a_diaconate_member(user)

            if membership:
                context['treasury_membership'] = True
        except Diaconate.DoesNotExist as e:
            context['treasury_diaconate_unavailable'] = True

        context['treasury_assets'] = Asset.objects.all()
        context['asset_categories'] = AssetCategory.objects.all()
        context['locations'] = [location[0] for location in LOCATION_CHOICES]
        context['conditions'] = [condition[0] for condition in CONDITION_CHOICES]
        context['source_of_items'] = [source[0] for source in SOURCE_OF_ITEM_CHOICES]
        context['statuses'] = [status[0] for status in STATUS_CHOICES]

        return context

    def post(self, request, **kwargs):
        
        context = {}
        
        asset_name = request.POST['asset_name'].strip()
        category = request.POST['category'].strip()
        purchase_date = request.POST['purchase_date'].strip()
        condition = request.POST['condition'].strip()
        source_of_item = request.POST['source_of_item'].strip()
        status = request.POST['status'].strip()
        location = request.POST['location'].strip()

        files = request.FILES.getlist('images', None)
        files_path = []
        
        if files:
            for file in files:
                relative_path = fr'{settings.MEDIA_URL}diaconate/Treasury/Inventory/{asset_name}'
                abs_path = fr"{settings.BASE_DIR}{relative_path}"
                if not os.path.isdir(abs_path):
                    os.makedirs(abs_path)  

                file_path = fr"{relative_path}/{file.name}"
                full_path = fr"{settings.BASE_DIR}{file_path}"
                
                file_path = AssetFile.objects.create(
                    name=file_path,
                    type=file.content_type,
                    size=file.size
                ) 
                files_path.append(file_path)
                 
                with open(full_path, 'wb') as f:
                    for chunk in file.chunks():
                        f.write(chunk)

        description = request.POST['asset_description']
        
        if 'edit' in request.GET:
            asset_id = request.GET['edit']
            asset = Asset.objects.get(id=asset_id)
            
            asset.name = asset_name
            asset.category = AssetCategory.objects.get(name=category)
            asset.purchase_date = purchase_date
            asset.condition = condition
            asset.source_of_item = source_of_item
            asset.status = status
            asset.location = location
            asset.description = description
            
            if files:
                asset.files.add(*files_path)
            
            try:
                asset.save()
            except Exception as e:
                context['confirm'] = False
                context['error_message'] = str(e)
            else:
                context['confirm'] = True
                context['success_message'] = "Asset successfully updated"

        
        else:            
            try:
                asset = Asset.objects.create(
                    name=asset_name,
                    category=AssetCategory.objects.get(name=category),
                    purchase_date=purchase_date,
                    condition=condition,
                    source_of_item=source_of_item,
                    status=status,
                    location=location,
                    description=description,
                )
                asset.files.add(*files_path)
                asset.save()
                
            except Exception as e:
                context['confirm'] = False
                context['error_message'] = str(e)

                context['treasury_assets'] = Asset.objects.all()
                
                if request.htmx:
                    return render(request, 'diaconate/treasury/partial_html/inventory_list_partial.html', context)
            else:
                context['confirm'] = True
                context['success_message'] = 'Asset successfully added to the database'
                
        if request.htmx:
            context['treasury_assets'] = Asset.objects.all()
            return render(request, 'diaconate/treasury/partial_html/inventory_list_partial.html', context)
        
        return HttpResponseRedirect(reverse_lazy('diaconate:treasury-inventory'))


class TreasuryPendingRequestView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = "diaconate/treasury/pending_request.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
            self.request.user.level == 'core_shep' 
                or self.request.user == 'chief_shep'
                    or is_member(self.request.user)):
            
            if 'pending-request-decision' in self.request.GET:
                pending_request_decision = self.request.GET['pending-request-decision']
                pending_request_id = self.request.GET['pending-request-id']

                pending_request = TreasuryRequest.objects.get(id=pending_request_id)
                if pending_request_decision == 'approve':
                    pending_request.status = 'Approved'
                    pending_request.approved_by = self.request.user
                    pending_request.approved_date = datetime.now().date().isoformat()
                    
                    # on approval change the asset location
                    pending_request.asset.location = pending_request.new_location
                    pending_request.asset.save()
                    
                elif pending_request_decision == 'reject':
                    pending_request.status = 'Rejected'
                
                
                pending_request.save()

                return JsonResponse({
                    'status': True,
                    'request_id': pending_request.id,
                })
                
            if 'download_requests' in self.request.GET:
                response = HttpResponse(
                    content_type="application/vnd.ms-excel",
                    charset='utf-8'
                )
                response['Content-Disposition'] = f'attachment; filename="pending_requests.xlsx"'
                
                data = TreasuryRequest.objects.values(
                    'id', 'requested_by__first_name', 'requested_by__last_name',
                    'new_location', 'department__department_name', 'asset__name',
                    'request_date', 'status', 'reason', 'approved_by__username',
                    'approved_date', 'preferred_date'
                )
                
                df = pd.DataFrame(data)
                df.columns = [
                    'ID', 'Requested by (First Name)', "Requested by (Last Name)",
                    "New Location", "Department Name", "Asset", "Request Date",
                    "Status", "Reason", "Approved By (Username)", "Approved Date",
                    "Request Deadline"
                ]
                
                df.to_excel(response, "pending_requests")
                
                return response
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden('You are not Authorized to come here...please Go back')

    def get_context_data(self, **kwargs) -> dict[str]:
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['category'] = 'Pending Request'
        context['page'] = 'Treasury'

        context['title'] = title
        context['user'] = user
        context['project_title'] = project_title

        # Context needed to handle the navigation menu

        department = DepartmentMember.objects.filter(member_name=user)
        
        if department:
            department = department.first().department_name

            
        if user.is_superuser:
            context['member_departments'] = Department.objects.all()
        else:
            context['member_departments'] = Department.objects.get_member_departments(user)
        context['department_leaders'] = [leader.member_name for leader in Department.objects.department_leaders() if leader]

        try:
            department_member = DepartmentMember.objects.get(member_name=user, department_name=department)
            context['department_membership'] = department_member
            context['is_department_leader'] = department.is_leader(department_member)
        except DepartmentMember.DoesNotExist:
            context['is_department_leader'] = False

        department_projects = DepartmentProject.objects.filter(department=department, status__in=['In Progress', 'Not Started'])
        context['department_projects'] = department_projects

        department_projects_status_statistic = DepartmentProject.objects.get_department_projects_status_statistic(department)
        context['department_project_status_statistic'] = department_projects_status_statistic

        all_department_pending_target = ProjectTarget.objects.all_department_pending_target(department)
        context['all_department_pending_target'] = all_department_pending_target

        # GET Member Activity in the project
        members, complete_project = department.member_activity_in_a_department()
        context['member_activity_in_a_department'] = zip(members, complete_project)

        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

        # end context for navigation menu

        # check if there is a treasury diaconate and adds a special link section
        # to access treasury related pages
        try:
            treasury = Diaconate.objects.get(name='TREASURY')
            membership = treasury.is_a_diaconate_member(user)

            if membership:
                context['treasury_membership'] = True
        except Diaconate.DoesNotExist as e:
            context['treasury_diaconate_unavailable'] = True

        treasury_requests = TreasuryRequest.objects.all()
        context['treasury_requests'] = treasury_requests
        

        return context

    def post(self, request, **kwargs):
        pass


class TreasuryMaintenanceView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = "diaconate/treasury/maintenance.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and (
            self.request.user.level == 'core_shep' 
                or self.request.user == 'chief_shep'
                    or is_member(self.request.user)):
            
            return super().get(request, *args, **kwargs)
        return HttpResponseForbidden('You are not Authorized to come here...please Go back')

    def get_context_data(self, **kwargs) -> dict[str]:
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['category'] = 'Maintenance'
        context['page'] = 'Treasury'

        context['title'] = title
        context['user'] = user
        context['project_title'] = project_title

        # Context needed to handle the navigation menu

        department = DepartmentMember.objects.filter(member_name=user)
        
        if department:
            department = department.first().department_name

            
        if user.is_superuser:
            context['member_departments'] = Department.objects.all()
        else:
            context['member_departments'] = Department.objects.get_member_departments(user)
        context['department_leaders'] = [leader.member_name for leader in Department.objects.department_leaders() if leader]

        try:
            department_member = DepartmentMember.objects.get(member_name=user, department_name=department)
            context['department_membership'] = department_member
            context['is_department_leader'] = department.is_leader(department_member)
        except DepartmentMember.DoesNotExist:
            context['is_department_leader'] = False

        department_projects = DepartmentProject.objects.filter(department=department, status__in=['In Progress', 'Not Started'])
        context['department_projects'] = department_projects

        department_projects_status_statistic = DepartmentProject.objects.get_department_projects_status_statistic(department)
        context['department_project_status_statistic'] = department_projects_status_statistic

        all_department_pending_target = ProjectTarget.objects.all_department_pending_target(department)
        context['all_department_pending_target'] = all_department_pending_target

        # GET Member Activity in the project
        members, complete_project = department.member_activity_in_a_department()
        context['member_activity_in_a_department'] = zip(members, complete_project)

        context['member_percentage'] = DepartmentProject.objects.calc_member_completed_percentage(user)

        # end context for navigation menu

        # check if there is a treasury diaconate and adds a special link section
        # to access treasury related pages
        try:
            treasury = Diaconate.objects.get(name='TREASURY')
            membership = treasury.is_a_diaconate_member(user)

            if membership:
                context['treasury_membership'] = True
        except Diaconate.DoesNotExist as e:
            context['treasury_diaconate_unavailable'] = True

        return context

