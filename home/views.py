from typing import Any
import numpy as np
import pandas as pd
from datetime import datetime

from django.utils import timezone
from django.urls import reverse_lazy
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseNotFound, HttpResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model

from django.core.exceptions import ValidationError

from .models import RecentActivity, BirthdayMessage, SuggestionComplaintMessage
from .models import Notification

from personal_development.models import BibleReading, PrayerMarathon
from church_work.models import ChurchWork
from evangelism.models import Evangelism

from users.models import (Catalog, Shepherd, SubShepherd, CustomUser,
                          Permission, FamilyMemberWeeklySchedule, Skill, Course)
from users.my_models.users import GENOTYPE_CHOICES, BLOOD_GROUP_CHOICES
from users.my_models.utilities import convert_image_to_webp

from project_management.models import DepartmentMember, Department
from pastoring.models import UrlShortener
from diaconate.models import AssetCategory, TreasuryRequest, Asset, LOCATION_CHOICES

from project_management.models import Diaconate


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
class Home(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/index.html'

    def get(self, request, *args, **kwargs):
        if 'mode' in kwargs:
            mode = kwargs['mode']

            if mode == 'suggestion_complaint':
                try:
                    title_ = request.GET['title']
                    category = request.GET['category']
                    level_of_urgency = request.GET['level_of_urgency']
                    message = request.GET['message']
                    is_anonymous = True if request.GET['is_anonymous'] == 'true' else False

                    user = request.user
                    shepherd = user.shepherd

                    if shepherd is None:
                        return JsonResponse({'confirm': False, 'error_message': "You don't have a shepherd!"})

                    suggestion_complaint = SuggestionComplaintMessage(title=title_, category=category,
                                                                      message=message, is_anonymous=is_anonymous,
                                                                      level_of_urgency=level_of_urgency,
                                                                      sender=user, receiver=shepherd)
                    suggestion_complaint.save()

                    # Send a notification to the user shepherd
                    notification = Notification(target=shepherd.name, mode='Suggestion/Complaint',
                                                activator=user, time_sensitivity='None', exposure_level='all',
                                                message=f"{user.username} has a {category}! [{level_of_urgency}]")
                    notification.save()

                except Exception as error:
                    return JsonResponse({'confirm': False, 'error_message': str(error)})
                else:
                    return JsonResponse({'confirm': True})
            elif mode == 'Notification':
                notification_id = int(kwargs['notification_id'])

                Notification.objects.get(id=notification_id).delete()

                return JsonResponse({})
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        recent = RecentActivity.custom_objects.auto_delete_old_activities(username=self.request.user)

        context['category'] = 'Homepage'
        context['developers'] = developers
        context['user'] = self.request.user
        context['title'] = title
        context['recent_activity'] = recent

        # Get all the active notification for the user
        general_notifications = Notification.objects.filter(target=self.request.user, exposure_level='general',
                                                           is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)
                                                        
        active_notifications = list(general_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        try:
            member_schedule = FamilyMemberWeeklySchedule.objects.get(username=self.request.user)
        except FamilyMemberWeeklySchedule.DoesNotExist:
            context['member_schedule'] = False
        else:
            context['member_schedule'] = True

            week_one = member_schedule.weekone
            week_two = member_schedule.weektwo
            week_three = member_schedule.weekthree
            week_four = member_schedule.weekfour

            context['week_one'] = week_one
            context['week_two'] = week_two
            context['week_three'] = week_three
            context['week_four'] = week_four

        # Check if user is in a department
        context['is_in_a_department'] = DepartmentMember.objects.is_in_a_department(context['user'])

        # Check which diaconate this user belongs to 
        diaconate = [diaconate for diaconate in Diaconate.objects.all() if diaconate.is_a_diaconate_member(context['user']) and diaconate.is_admin_staff(context['user'])]
        context['diaconate_membership'] = diaconate

        return context


class Profile(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/app/user-profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Profile'
        context['developers'] = developers
        context['user'] = self.request.user
        context['title'] = title

        context['shepherd'] = Shepherd.objects.all().exclude(name=self.request.user)
        context['sub_shepherd'] = SubShepherd.objects.all().exclude(name=self.request.user)

        context['genotype'] = GENOTYPE_CHOICES
        context['blood_group'] = BLOOD_GROUP_CHOICES
        context['celebrant'] = get_user_model().objects.get_today_birthday()
        context['celebrant_birthday_messages'] = BirthdayMessage.objects.get_user_birthday_message(self.request.user)

        # Get all the active notification for the user
        general_notifications = Notification.objects.filter(target=self.request.user, exposure_level='general',
                                                           is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)
                                                        
        active_notifications = list(general_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        context['is_profile_updated'] = self.request.user
        context['skills'] = Skill.objects.all()
        context['courses'] = Course.objects.all()

        employment_status = [
            'Employed', 'Employed but still looking for another job',
            'Under Employed', 'Unemployed'
        ]
        context['employment_status'] = employment_status

        return context

    def get(self, request, *args, **kwargs):
        if 'birthday_message' in request.GET:
            try:
                sender = get_user_model().objects.get(username=request.GET['sender'])
                receiver = get_user_model().objects.get(username=request.GET['receiver'])
                message = request.GET['message']

                birthday_message = BirthdayMessage(sender=sender, receiver=receiver, message=message)
                birthday_message.save()

                notification = Notification(target=receiver, mode='Birthday',
                                           activator=sender, time_sensitivity='None', 
                                           exposure_level='general', 
                                           message=f"{sender.username} sends birthday wishes")
                
                notification.save()

            except Exception:
                return JsonResponse({'confirm': False})
            else:
                return JsonResponse({'confirm': True})
        elif 'check_birthday_message' in request.GET:
            sender = get_user_model().objects.get(username=request.GET['sender'])
            receiver = get_user_model().objects.get(username=request.GET['receiver'])

            try:
                well_wishing = BirthdayMessage.objects.get(sender=sender, receiver=receiver)
            except BirthdayMessage.DoesNotExist:
                return JsonResponse({'confirm': False})
            else:
                return JsonResponse({'confirm': True})
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request, **kwargs) -> HttpResponse:
        context = self.get_context_data(**kwargs)
        form = request.POST['form_name']

        if form.lower().strip() == 'password':
            current_password = request.POST['current_password']
            new_password = request.POST['new_password']
            # get user using password as a means of confirmation

            user = request.user

            if not user.check_password(current_password):
                context['password_update'] = 'failed'

                if request.htmx:
                    return render(request, 'dashboard/app/partial_html/change_password.html', context)
                return self.render_to_response(context)

            user.set_password(new_password)
            user.save()

            recent = RecentActivity.objects.create(
                username=request.user,
                category="bio_data",
                details='Changed Password'
            )

            context['password_update'] = 'successful'

            if request.htmx:
                return render(request, 'dashboard/app/partial_html/change_password.html', context)
            return self.render_to_response(context)

        elif form.lower().strip() == 'profile':

            user: CustomUser = request.user

            # BIO DATA

            user.first_name = request.POST['first_name'].strip()
            user.last_name = request.POST['surname'].strip()
            user.gender = request.POST['gender'].strip()

            # validate and set the date of birth
            try:
                user.set_date_of_birth(request.POST['date_of_birth'])
            except ValidationError:
                return JsonResponse({'error': "Your birth date should not be now or in the future"})

            user.about = request.POST['about']

            # PERSONAL DATA
            user.phone_number = request.POST.get('phone_number', '').strip()
            user.occupation = request.POST.get('occupation', '').strip()
            user.address = request.POST['address'].strip()
            user.marital_status = request.POST['marital_status']

            user.employment_status = request.POST['employment_status']

            skills = request.POST.getlist('skills')
            skills = ", ".join(skills)
            user.skills = skills

            # BASIC MEDICAL INFORMATION
            user.blood_group = request.POST['blood_group']
            user.genotype = request.POST['genotype']
            user.chronic_illness = request.POST['chronic_illness'].strip()

            # RESIDENTIAL INFORMATION
            user.lga = request.POST['lga'].strip()
            user.state = request.POST['state'].strip()
            user.country = request.POST['country'].strip()
            user.church_outpost = request.POST['church_outpost'].strip()

            # SCHOOL INFORMATION
            user.course_of_study = request.POST['course_of_study'].strip()
            user.years_of_study = request.POST['years_of_study'].strip()
            user.current_year_of_study = request.POST['current_year_of_study'].strip()
            user.final_year_status = request.POST['final_year_status'].strip()
            
            graduate_status = request.POST['graduate_status'].strip()
            if graduate_status:
                user.graduate_status = graduate_status
            else:
                user.graduate_status = None

            # NEXT OF KIN INFORMATION
            user.next_of_kin_full_name = request.POST['next_of_kin_full_name'].strip()
            user.next_of_kin_relationship = request.POST['next_of_kin_relationship'].strip()
            user.next_of_kin_phone_number = request.POST['next_of_kin_phone_number'].strip()
            user.next_of_kin_address = request.POST['next_of_kin_address'].strip()

            # SPIRITUAL INFORMATION
            user.gift_graces = request.POST['gift_graces'].strip()

            # ADDITIONAL INFORMATION
            user.unit_of_work = request.POST['unit_of_work'].strip()

            shepherd = request.POST['shepherd'].strip()
            if shepherd:
                shepherd = get_user_model().objects.get(username=request.POST['shepherd'])
                shepherd = Shepherd.objects.get(name=shepherd)
                user.shepherd = shepherd
            else:
                user.shepherd = None

            sub_shepherd = request.POST['sub_shepherd'].strip()
            if sub_shepherd:
                sub_shepherd = get_user_model().objects.get(username=request.POST['sub_shepherd'])
                sub_shepherd = SubShepherd.objects.get(name=sub_shepherd)
                user.sub_shepherd = sub_shepherd
            else:
                user.sub_shepherd = None

            # SPECIAL KNOWLEDGE
            user.shoe_size = request.POST['shoe_size']
            user.cloth_size = request.POST['cloth_size']

            try:
                profile_pic = request.FILES['profile_pic']
                profile_pic_webp = convert_image_to_webp(profile_pic)

                user.profile_pic = profile_pic_webp
            except Exception as e:
                pass

            user.set_profile_update_status()

            user.save()

            # update relevant data
            if shepherd:
                shepherd.no_of_sheep = shepherd.get_no_of_sheep()
                shepherd.save()
            if sub_shepherd:
                sub_shepherd.no_of_sheep = sub_shepherd.get_no_of_sheep()
                sub_shepherd.save()

            recent = RecentActivity(username=request.user, category="bio_data",
                                    details='Updated Bio Data')
            recent.save()

            context['profile_update'] = 'successful'
            return self.render_to_response(context)


class CatalogView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/table/catalog_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Catalog'
        context['developers'] = developers
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

    def get(self, request, *args, **kwargs):
        if 'unique_id' in request.GET:
            unique_id = request.GET['unique_id']

            try:
                catalog = Catalog.objects.get(id=unique_id)
            except Catalog.DoesNotExist:
                return JsonResponse({'confirm': False})
            else:

                return JsonResponse({'confirm': True, 'catalog': catalog.get_cleaned_fields_in_dict()})
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request, **kwargs) -> HttpResponse:
        context = super().get_context_data(**kwargs)
        context['category'] = 'Catalog'
        context['developers'] = developers
        context['user'] = self.request.user
        context['title'] = title

        search_text = request.POST['search_text']

        results = Catalog.objects.filter(things_spoken_about__icontains=search_text)
        context['results'] = results
        context['no_of_results'] = len(results)
        context['search_text'] = search_text

        return self.render_to_response(context)


class TaskView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/special-pages/tasks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category'] = 'Task'
        context['developers'] = developers
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


class SuggestionComplaintView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'dashboard/table/suggestion_complaint_table_data.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        mode = kwargs['mode']

        if mode == 'Shepherd':
            self.template_name = 'pastoring/suggestion_complaint.html'

    def get(self, request, *args, **kwargs):
        if 'message_seen' in request.GET:
            message_id = int(request.GET['message_id'])

            suggestion_complaint = SuggestionComplaintMessage.objects.get(id=message_id)
            suggestion_complaint.message_seen = True
            suggestion_complaint.save()

            return JsonResponse({})
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['developers'] = developers
        context['title'] = title

        mode = kwargs['mode']
        context['mode'] = mode
        context['category'] = 'Suggestion/Complaint'

        if mode == 'Personal':
            suggestions = SuggestionComplaintMessage.objects.filter(sender=self.request.user, category='Suggestion')
            complaints = SuggestionComplaintMessage.objects.filter(sender=self.request.user, category='Complaint')

            context['suggestions'] = suggestions
            context['complaints'] = complaints

            # Get all the active notification for the user
            general_notifications = Notification.objects.filter(target=self.request.user, exposure_level='general',
                                                            is_activated=False)
            all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                            is_activated=False)
                                                            
            active_notifications = list(general_notifications) + list(all_notifications)
            context['active_notifications'] = active_notifications
            context['no_of_notifications'] = len(active_notifications)

        elif mode == "Shepherd":
            shepherd = Shepherd.objects.get(name=self.request.user)

            # Get all the active notification for the user
            pastoral_notifications = Notification.objects.filter(target=self.request.user, exposure_level='pastoral',
                                                            is_activated=False)
            all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                            is_activated=False)
                                                            
            active_notifications = list(pastoral_notifications) + list(all_notifications)
            context['active_notifications'] = active_notifications
            context['no_of_notifications'] = len(active_notifications)

            if 'chief_shep_bypass' in self.request.GET:
                chief_shep_bypass = True
                shepherd_id = self.request.GET['shepherd_id']
                shepherd = Shepherd.objects.get(id=shepherd_id)
            else:
                chief_shep_bypass = False

            if self.request.user.level == 'core_shep' or chief_shep_bypass:
                suggestions_complaints = SuggestionComplaintMessage.objects.retrieve_sheep_suggestions_complaints(shepherd)

                suggestions = suggestions_complaints.filter(category='Suggestion').order_by('level_of_urgency', 'sender')
                complaints = suggestions_complaints.filter(category='Complaint').order_by('level_of_urgency', 'sender')

                context['suggestions'] = suggestions
                context['complaints'] = complaints
                context['chief_shep_bypass'] = chief_shep_bypass

            elif self.request.user.level == 'chief_shep':
                receivers_dict = SuggestionComplaintMessage.objects.retrieve_suggestions_complaints_statistics()

                context['receivers_dict'] = receivers_dict

        return context


class Registration(TemplateView):
    template_name = 'dashboard/auth/sign-up.html'

    def get_context_data(self, **kwargs):
        context = super(Registration, self).get_context_data(**kwargs)
        context['developers'] = developers
        context['title'] = title

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)

        first_name = request.POST['first_name'].strip().lower()
        surname = request.POST['last_name'].strip().lower()
        username = request.POST['username'].strip()
        gender = request.POST['gender'].strip()
        password = request.POST['password'].strip()

        email = request.POST['email'].strip().lower()
        phone_number = request.POST['phone_number'].strip()

        user = get_user_model().objects.create_user(email=email, password=password, save=False,
                                                    first_name=first_name, last_name=surname,
                                                    username=username, gender=gender, phone_number=phone_number
                                                    )

        try:
            user.save()
        except BaseException as e:
            error = str(e)
            if 'email' in error:
                context['error'] = "This email already have an account"
            else:
                context['error'] = f"This username '{username}' is already taken"
            return self.render_to_response(context)

        # Save the this specific user's permission
        # permissions = Permission(name=user, can_edit_catalog=False,
        #                          head_of_department=False)
        #
        # permissions.save()

        login(request, user)
        return HttpResponseRedirect(reverse_lazy('home'))


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('users-login'))


class Login(TemplateView):
    template_name = 'dashboard/auth/sign-in.html'

    def get_context_data(self, **kwargs):
        context = super(Login, self).get_context_data(**kwargs)
        context['developers'] = developers
        context['title'] = title

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        email_username = request.POST['email_username'].strip()
        password = request.POST['password'].strip()

        User = get_user_model()
        
        try:
            user = User.objects.get(email=email_username.lower())
        except User.DoesNotExist:
            user = None
        else:
            confirm_password = user.check_password(password)
            
            if not confirm_password:
                user = None

        if user is None:
            # Username is used for login
            try:
                user = User.objects.get(username=email_username)
            except User.DoesNotExist:
                context['error'] = True
                return self.render_to_response(context)

            confirm_password = user.check_password(password)

            if not confirm_password:
                context['error'] = True
                return self.render_to_response(context)

        login(request, user)
        return HttpResponseRedirect(reverse_lazy('home'))


class RecoverPasswordView(TemplateView):
    template_name = 'dashboard/auth/recoverpw.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['developers'] = developers
        context['title'] = title

        return context
    
    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        new_password = request.POST['new_password']

        # Validate if user is correct
        try:
            user = CustomUser.objects.get(
                email=email, first_name=first_name,
                last_name=last_name
            )
        except CustomUser.DoesNotExist:
            user = None

        if user:
            user.set_password(new_password)
            user.save()
            return JsonResponse({'confirm': True})
        else:
            return JsonResponse({'confirm': False})


class TreasuryRequestView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('users-login')
    template_name = 'diaconate/treasury/treasury_request_form.html'
    
    def get(self, request, *args, **kwargs):
        
        if request.htmx:
            if 'slider' in request.GET:
                asset = request.GET['asset'].strip()
                context = {}
                if asset and asset.lower() != 'none':
                    asset = Asset.objects.get(id=asset)
                    context['asset'] = asset
                else:
                    context['asset'] = None
                    
                return render(request, 'diaconate/treasury/partial_html/asset_image_changer_for_request_form.html', context)
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = title
        context['category'] = 'Treasury Request Form'
        context['developers'] = developers
        context['user'] = self.request.user

        # Get all the active notification for the user
        general_notifications = Notification.objects.filter(target=self.request.user, exposure_level='general',
                                                           is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)
                                                        
        active_notifications = list(general_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        # load to the context the information gotten from the query 
        # parameters

        if 'confirm_request' in self.request.GET:
            confirm_request = self.request.GET['confirm_request']
            context['confirm_request'] = confirm_request

            if confirm_request == 'failed':
                context['error_message'] = self.request.GET['error_message']

        # Ensure that the treasury diaconate has been created before the page
        # is loaded, else display a warning page to create the diaconate

        try:
            treasury = Diaconate.objects.get(name='TREASURY')
        except Diaconate.DoesNotExist as e:
            context['treasury_diaconate_unavailable'] = True
            return context
        else:
            context['treasury'] = treasury
        
        context['asset_categories'] = AssetCategory.objects.all()
        context['assets'] = Asset.objects.all()
        context['locations'] = LOCATION_CHOICES
        return context
    
    def post(self, request, **kwargs) -> HttpResponse:
        context = super().get_context_data(**kwargs)

        requester_name = request.POST['requester_name']
        department = request.POST.get('department', False)

        if not department:
            confirm_request = 'failed'
            error_message = 'You must belong in a department before you can make a request'
            
            return HttpResponseRedirect(f"{reverse_lazy('treasury-request-form')}?confirm_request={confirm_request}&error_message={error_message}")
        else:
            department = Department.objects.get(id=department)

        asset = request.POST.get('asset', False).strip()

        if not asset:
            context['confirm_request'] = 'failed'
            context['error_message'] = 'Asset cannot be empty!' 
            return HttpResponseRedirect(f"{reverse_lazy('treasury-request-form')}?confirm_request=failed&error_message={error_message}")
        else: 
            asset = Asset.objects.get(id=asset)
         
        new_location = request.POST['new_location']
        request_deadline = request.POST['request_deadline']

        if request_deadline:
            request_deadline = datetime.fromisoformat(request_deadline)
        else:
            request_deadline = None

        justification = request.POST['justification'].strip()

        if not justification:
            confirm_request = 'failed'
            error_message = "Please enter your reason for your request"

            return HttpResponseRedirect(f"{reverse_lazy('treasury-request-form')}?confirm_request={confirm_request}&error_message={error_message}")

        try:
            TreasuryRequest.objects.create(
                requested_by=request.user,
                department=department,
                asset=asset,
                reason=justification,
                preferred_date=request_deadline,
                new_location=new_location
            )
        except Exception as e:
            context['confirm_request'] = 'failed'
            context['error_message'] = str(e)
            
            return HttpResponseRedirect(f"{reverse_lazy('treasury-request-form')}?confirm_request={confirm_request}&error_message={str(e)}")
        return HttpResponseRedirect(f"{reverse_lazy('treasury-request-form')}?confirm_request=success")


class TreasuryRequestListView(LoginRequiredMixin, TemplateView):
    template_name = 'diaconate/treasury/treasury_request_list.html'
    login_url = reverse_lazy('users-login')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['title'] = title
        context['category'] = 'Treasury Request Form'
        context['developers'] = developers
        context['user'] = self.request.user

        # Get all the active notification for the user
        general_notifications = Notification.objects.filter(target=self.request.user, exposure_level='general',
                                                           is_activated=False)
        all_notifications = Notification.objects.filter(target=self.request.user, exposure_level='all',
                                                        is_activated=False)
                                                        
        active_notifications = list(general_notifications) + list(all_notifications)
        context['active_notifications'] = active_notifications
        context['no_of_notifications'] = len(active_notifications)

        # retrieve the request made by this user
        treasury_requests = TreasuryRequest.objects.filter(requested_by=self.request.user)
        context['treasury_requests'] = treasury_requests

        return context


class ComingSoonView(TemplateView):
    template_name = 'dashboard/coming_soon.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = title

        category = kwargs['category']

        if category == 'Shepherd Report':
            context['page_title'] = 'Shepherd Report'
            context['page_content'] = "Write your report and your shepherd immediately get notified"

        elif category == 'Suggestion Box':
            context['page_title'] = 'Suggestion Box'
            context['page_content'] = "Send suggestions or complaints directly to your shepherd anonymously or not"

        return context

# @@@@@@@############@############################################

# UPDATE DASHBOARD COUNTER

# ##########################@@@@@@@@@@@@@@@@@@@@@@@@


class CounterUpdate(LoginRequiredMixin, TemplateView):
    """
    Return the total number of passages or prayers that has been read by
    the user
    """
    login_url = reverse_lazy('users-login')

    def get(self, request, **kwargs):
        bible_reading = BibleReading.objects.filter(username=request.user)
        prayer_marathon = PrayerMarathon.objects.filter(username=request.user)
        church_work = ChurchWork.objects.filter(username=request.user)
        evangelism = Evangelism.objects.filter(username=request.user)

        context = {
            'counter_passages': bible_reading.count(),
            'counter_prayers': prayer_marathon.count(),
            'counter_church_works': church_work.count(),
            'counter_evangelism': evangelism.count()
        }

        return JsonResponse(context)


class ChartBibleReading(LoginRequiredMixin, TemplateView):
    """
    Return the total number of passages or prayers that has been read by
    the user
    """
    login_url = reverse_lazy('users-login')

    def get(self, request, **kwargs):
        category = kwargs['category']
        mode = kwargs['mode']

        context = {
            'category': category,
            'mode': mode
        }
        if category == 'All':
            bible_reading_dates = BibleReading.data_analysis.date_series(request.user)
            prayer_marathon_dates = PrayerMarathon.data_analysis.date_series(request.user)

            return JsonResponse(context)

        elif category == 'Bible Reading':
            dates = BibleReading.data_analysis.date_series(request.user)

        elif category == 'Prayer Marathon':
            dates = PrayerMarathon.data_analysis.date_series(request.user)

        elif category == 'Church Work':
            dates = ChurchWork.data_analysis.date_series(request.user)

        elif category == 'Evangelism':
            fields = [
                'no_of_people_prayed', 'no_led_to_christ',
                'follow_up', 'holy_spirit_baptism'
            ]
            motivator = Evangelism.objects.filter(username=request.user).values_list('no_of_people_prayed',
                                                                                     'no_led_to_christ',
                                                                                     'follow_up', 'holy_spirit_baptism')
            denominator = 1000
            percent = 100

            people_prayed = int(sum(motivator.values_list('no_of_people_prayed', flat=True)))
            led_to_christ = int(sum(motivator.values_list('no_led_to_christ', flat=True)))
            follow_up = int(sum(motivator.values_list('follow_up', flat=True)))
            baptism = int(sum(motivator.values_list('holy_spirit_baptism', flat=True)))

            people_prayed_percentage = (people_prayed / denominator) * percent
            led_to_christ_percentage = (led_to_christ / denominator) * percent
            follow_up_percentage = (follow_up / denominator) * percent
            baptism_percentage = (baptism / denominator) * percent

            raw = [people_prayed, led_to_christ, follow_up, baptism]
            values = [people_prayed_percentage, led_to_christ_percentage,
                      follow_up_percentage, baptism_percentage]

            context['distinct_values'] = fields
            context['unique_counts'] = values
            context['raw_values'] = raw

            return JsonResponse(context)

        else:
            # pass
            assert False, "You are not suppose to be here"

        if dates.empty:
            if mode == 'daily':
                context['distinct_values'] = list(days.keys())
                context['unique_counts'] = [0] * len(days.keys())
            elif mode == 'monthly':
                context['distinct_values'] = list(months.keys())
                context['unique_counts'] = [0] * len(months.keys())
            elif mode == 'monthly':
                context['distinct_values'] = [' ', ' ']
                context['unique_counts'] = [0, 0]

            return JsonResponse(context)

        if mode == 'daily':
            dates = dates.strftime('%a')
        elif mode == 'monthly':
            dates = dates.strftime('%b')
        elif mode == 'yearly':
            dates = dates.strftime('%Y')

        distinct_values, unique_counts = np.unique(dates, return_counts=True)

        data = {
            'distinct_values': distinct_values,
            'unique_counts': unique_counts
        }

        df = pd.DataFrame(data)

        if mode == 'daily' or mode == 'monthly':
            df = df.sort_values(by='distinct_values', key=sort_function)
        elif mode == 'yearly':
            df = df.sort_values(by='distinct_values')

        context['distinct_values'] = list(df['distinct_values'])
        context['unique_counts'] = [int(x) for x in df['unique_counts']]

        return JsonResponse(context, safe=False)



# ######################################################

# SHORT LINKS

def short_links(request):

    shortened_url = request.get_full_path()[1:]

    try:
        url = UrlShortener.objects.get(shortened_url=shortened_url) 
        url.click_count += 1
        url.save()

        if not url.is_active:
            raise UrlShortener.DoesNotExist
        if url.expires_at:
            if url.expires_at < timezone.now():
                raise UrlShortener.DoesNotExist
    except UrlShortener.DoesNotExist as e:
        return HttpResponseNotFound()

    return HttpResponseRedirect(redirect_to=url.original_url)

# #######################################################