from django.contrib import admin
from .models import (Testimony, PropheticWord, Sermon, Blog, UrlShortener)


# Register your models here.
@admin.register(Testimony)
class TestimonyAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'category', 'testifier')
    list_filter = ('category', 'testifier')
    date_hierarchy = 'date'
    search_fields = ('title', 'testifier')


@admin.register(PropheticWord)
class PropheticWordAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'category', 'speaker')
    list_filter = ('category', 'speaker')
    date_hierarchy = 'date'
    search_fields = ('title', 'speaker')


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'author')
    list_filter = ('author', )
    date_hierarchy = 'date'


@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'category', 'download_link')
    list_filter = ('category', )
    search_fields = ('title', )
    date_hierarchy = 'date'


@admin.register(UrlShortener)
class UrlShortenerAdmin(admin.ModelAdmin):
    list_display = ('shortened_url', 'original_url', 'click_count', 'expires_at')
    search_fields = ('shortened_url', 'original_url', )
