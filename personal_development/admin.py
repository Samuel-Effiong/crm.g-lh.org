from django.contrib import admin

from .models import PrayerMarathon, BibleReading
from .models import ShepherdReport


# Register your models here.
@admin.register(PrayerMarathon)
class PrayerMarathonAdmin(admin.ModelAdmin):
    list_display = ('username', 'date', 'trunc_comment')
    list_filter = ('username', 'date',)
    search_fields = ('comments', )
    ordering = ('-date',)
    date_hierarchy = 'date'


@admin.register(BibleReading)
class BibleReadingAdmin(admin.ModelAdmin):
    list_display = ('username', 'bible_passage', 'date', 'status')
    list_filter = ('username', 'date', 'status')
    ordering = ('-date',)
    date_hierarchy = 'date'


@admin.register(ShepherdReport)
class ShepherdReportAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'date')
    ordering = ('-date', )
    date_hierarchy = 'date'
