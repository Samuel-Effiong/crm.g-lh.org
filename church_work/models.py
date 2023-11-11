
from django.conf import settings
from django.db import models

from django.urls import reverse
from django.utils import timezone

import pandas as pd


DEFAULT = 0
STATUS = (
    ('transcription', 'Transcription'),
    ('video_editing', 'Video Editing'),
    ('building', 'Building'),
    ('extraction', 'Extraction'),
    ('audio_editing', 'Audio Editing'),
    ('audio_video_review', 'Audio/Video Review'),
    ('audio_video_snippets', 'Audio/Video Snippets')
)


class DataAnalysisManager(models.Manager):
    # def get_queryset(self):
    #     return super(DataAnalysisManager, self).get_queryset().filter(username=settings.AUTH_USER_MODEL)

    def date_series(self, user) -> pd.DatetimeIndex:
        object = self.get_queryset().filter(username=user).values_list('date', flat=True)

        return pd.to_datetime(object)


# Create your models here.
class ChurchWork(models.Model):
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field='username')

    work_category = models.CharField(max_length=100, choices=STATUS)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)

    details = models.TextField()
    hours_spent = models.IntegerField(default=DEFAULT)

    last_active_date = models.DateField('Last active date', default=timezone.now)

    objects = models.Manager()
    data_analysis = DataAnalysisManager()

    def __str__(self):
        return f"Work done on {self.work_category} at {self.date.strftime('%a %d %b %Y')}"

    def get_absolute_url(self):
        return reverse('church_work:detail', args=[self.id])

    class Meta:
        ordering = ('-date',)
