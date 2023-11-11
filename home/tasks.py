# from background_task import background
# from .signals import birthday_signal

# from django.contrib.auth import get_user_model
# from django.utils import timezone

# from datetime import timedelta

# from .models import Notification


# # Schedule background task to start at midnight
# current_datetime = timezone.now()
# hour = current_datetime.hour
# minute = current_datetime.minute

# from_midnight = 23 - hour
# from_midnight_minute = 60 - minute
# delta = timedelta(hours=from_midnight, minutes=from_midnight_minute)

# @background(schedule=current_datetime + delta)
# def system_wide_tasks():
#     update_birthday_notification()
#     clean_outdated_notification()


# def update_birthday_notification():
#     active_celeb = get_user_model().objects.get_today_birthday()

#     if active_celeb:
#         no_of_celeb = len(active_celeb)

#         # Send to all the users
#         all_users = get_user_model().objects.all()

#         message = f"{no_of_celeb} Brethren have birthdays TODAY!"

#         for user in all_users:
#             notification = Notification(target=user, mode='Birthday', 
#                                         exposure_level='general',
#                                         message=message, time_sensitivity='1 DAY')
            
#             notification.save()


# def clean_outdated_notification():
#     outdated_notification = Notification.objects.filter(time_sensitivity='1 DAY')

#     if outdated_notification:
        
#         for notification in outdated_notification:
#             date_activated = notification.date_activated.day
#             current_date = timezone.now().day

#             time_difference = current_date - date_activated

#             if time_difference > 1:
#                 Notification.objects.get(id=notification.id).delete()






    

