from django.conf import settings
from django.db import models

from django.urls import reverse
from django.utils import timezone
import pandas as pd


DEFAULT = 0


class DataAnalysisManager(models.Manager):
    # def get_queryset(self):
    #     return super(DataAnalysisManager, self).get_queryset().filter(username=settings.AUTH_USER_MODEL)

    def date_series(self, user) -> pd.DatetimeIndex:
        object = self.get_queryset().filter(username=user).values_list('', flat=True)

        return pd.to_datetime(object)


# Create your models here.
class Evangelism(models.Model):
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field='username')
    field_of_visit = models.CharField(max_length=300)
    hours_spent_per_week = models.PositiveIntegerField(default=DEFAULT)
    no_led_to_christ = models.PositiveIntegerField(default=DEFAULT)
    follow_up = models.PositiveIntegerField(default=DEFAULT)
    invitees = models.PositiveIntegerField(default=DEFAULT)
    holy_spirit_baptism = models.PositiveIntegerField(default=DEFAULT)
    no_of_people_prayed = models.PositiveIntegerField(default=DEFAULT)
    prints_shared = models.PositiveIntegerField(default=DEFAULT)
    messages = models.TextField()
    snippets = models.PositiveIntegerField(default=DEFAULT)

    first_date_of_week = models.DateField(default=timezone.now)
    last_date_of_week = models.DateField(default=timezone.now)

    objects = models.Manager()
    data_analysis = DataAnalysisManager()

    def __str__(self):
        return f"Lead {self.no_led_to_christ} to Christ"

    def get_absolute_url(self):
        return reverse('evangelism:detail', args=[self.id])

    class Meta:
        ordering = ('-no_led_to_christ',)
