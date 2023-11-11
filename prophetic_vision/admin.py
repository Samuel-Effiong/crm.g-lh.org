from django.contrib import admin
from .models import PropheticVision

# Register your models here.


@admin.register(PropheticVision)
class PrayerMarathonAdmin(admin.ModelAdmin):
    list_display = ('username', 'title', 'date')
    list_filter = ('username', 'date')
    ordering = ('-date',)
    date_hierarchy = 'date'
