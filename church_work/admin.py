from django.contrib import admin
from .models import ChurchWork


# Register your models here.

@admin.register(ChurchWork)
class ChurchWorkAdmin(admin.ModelAdmin):
    list_display = ('username', 'work_category', 'date')
    list_filter = ('date', 'work_category')
    date_hierarchy = 'date'
