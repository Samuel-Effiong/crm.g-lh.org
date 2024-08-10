import os
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from wagtail.fields import RichTextField
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel


class Utility:
    def formatted_date(self):
        return self.date.isoformat()


# Create your models here.
# ########################### WORKSPACE MODELS  ###################################
class TestimonyManager(models.Manager):
    def retrieve_unique_testifiers(self):
        query = self.get_queryset().values_list('testifier', flat=True)
        return query


class SermonManager(models.Manager):
    def retrieve_unique_sermon_series(self):
        query = self.get_queryset().values_list('series_title', flat=True)
        return query


class PropheticWordManager(models.Manager):
    def retrieve_unique_speakers(self):
        query = self.get_queryset().values_list('speaker', flat=True)
        return query


@register_snippet
class Testimony(models.Model, Utility):
    TESTIMONY_CATEGORY = (
        ('life', 'Life Testimony'),
        ('general', 'General Testimony'),
        ('evangelism', 'Evangelism Testimony')
    )

    title = models.CharField(max_length=1000)
    testifier = models.CharField(max_length=255)
    date = models.DateField(default=timezone.now)

    category = models.CharField(choices=TESTIMONY_CATEGORY, max_length=50)
    message = models.TextField()

    objects = TestimonyManager()

    class Meta:
        verbose_name_plural = 'Testimonies'
        ordering = ('-date', )

    def __str__(self) -> str:
        return self.title


@register_snippet
class PropheticWord(models.Model, Utility):
    PROPHETIC_CATEGORY = (
        ('church', 'WORDS FOR THE CHURCH'),
        ('nigeria', 'WORDS FOR NIGERIA'),
        ('season', 'WORDS FOR THE SEASON'),
        ('general', 'GENERAL WORDS')
    )

    category = models.CharField(max_length=50, choices=PROPHETIC_CATEGORY)
    title = models.CharField(max_length=1000)
    date = models.DateField(default=timezone.now)
    speaker = models.CharField(max_length=255)
    message = models.TextField()
    ai_generated_summary = models.TextField(blank=True, null=True)
    ai_generated_keywords = models.TextField(blank=True, null=True)

    objects = PropheticWordManager()

    class Meta:
        ordering = ('-date', )
        verbose_name_plural = 'Prophetic Words'

    def __str__(self) -> str:
        return self.title


@register_snippet
class Blog(models.Model, Utility):
    title = models.CharField(max_length=1000)
    date = models.DateField(default=timezone.now)
    message = models.TextField()
    author = models.CharField(max_length=255)

    class Meta:
        ordering = ('-date', )

    def __str__(self) -> str:
        return self.title


@register_snippet
class Sermon(models.Model, Utility):
    SERMONS_CATEGORIES = (
        ('audio_series', 'Audio Sermon Series'),
        ('audio_single', 'Audio Single Sermons'),
        ('sermon_videos', 'Sermon Videos'),
        ('fars', 'FARS Seminar'),
    )

    title = models.CharField(max_length=1000)
    series_title = models.CharField(
        max_length=1000, blank=False, null=True,
        help_text="The Series the sermon belongs to if it is not single"
    )

    category = models.CharField(max_length=50, choices=SERMONS_CATEGORIES)
    date = models.DateField(default=timezone.now)
    download_link = models.URLField()

    objects = SermonManager()

    class Meta:
        ordering = ('-date', )

    def __str__(self) -> str:
        return self.title


class UrlShortener(models.Model, Utility):
    original_url = models.URLField(unique=True)
    shortened_url = models.CharField(max_length=1000, unique=True)
    created_at = models.DateField(auto_now_add=True)
    expires_at = models.DateField(null=True, blank=True)
    click_count = models.IntegerField(default=0)
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.shortened_url} -> {self.original_url}"
    
    def to_json(self):
        data = {
            'id': self.id,
            'original': self.original_url,
            'short': self.shortened_url,
            'date': self.created_at.isoformat(),
            'expired_date': self.expires_at.isoformat() if self.expires_at else "",
            'click_count': self.click_count,
            'user': str(self.user),
            'is_active': self.is_active
        }

        return data
