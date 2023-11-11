from django.contrib import admin
from .models import RecentActivity, BirthdayMessage, SuggestionComplaintMessage
from .models import Notification

@admin.register(RecentActivity)
class RecentActivityAdmin(admin.ModelAdmin):
    list_display = ('username', 'date', 'category')
    list_filter = ('username', 'category')

    # FIXME: ADD FUNCTIONALITY TO DELETE THE OLDEST ROW IF IT EXCEEDS 10 ENTRIES
    # FIXME: FOR A PARTICULAR USER.

    #DONE


@admin.register(BirthdayMessage)
class BirthdayMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'date')
    list_filter = ('date',)
    date_hierarchy = 'date'


@admin.register(SuggestionComplaintMessage)
class SuggestionComplaintMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'category', 'title',)
    list_filter = ('category', 'level_of_urgency', 'is_anonymous', 'message_seen')
    date_hierarchy = 'date_sent'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('target', 'mode', 'activator', 'is_activated')
    list_filter = ('is_activated', 'mode')
