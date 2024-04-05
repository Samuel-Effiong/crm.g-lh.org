from typing import Tuple, Dict
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models

from django.urls import reverse
from django.utils import timezone

import numpy as np
import pandas as pd

from users.models import Shepherd

DEFAULT = 0
STATUS = (
    ('completed', 'Completed'),
    ('in_progress', 'In Progress'),
    ('not_started', 'Not Started')
)


class DataAnalysisManager(models.Manager):

    def date_series(self, user) -> pd.DatetimeIndex:
        object = self.get_queryset().filter(username=user).values_list('date', flat=True)

        return pd.to_datetime(object)


# Create your models here.
class BibleReading(models.Model):
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)

    bible_passage = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=STATUS)
    comment = models.TextField()

    objects = models.Manager()
    data_analysis = DataAnalysisManager()

    def __str__(self):
        return f"{self.bible_passage} - {self.status}"

    def get_absolute_url(self):
        return reverse('bible_reading:detail',
                       args=[self.bible_passage, self.id])

    class Meta:
        ordering = ('-date', )


class PrayerMarathon(models.Model):
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    date = models.DateField(default=timezone.now)

    objects = models.Manager()
    data_analysis = DataAnalysisManager()

    def __str__(self):
        return f"Prayer Marathon on {self.date.strftime('%a %d %b %Y')}"

    @admin.display(description="Comment")
    def trunc_comment(self):
        return f"{self.comment[:20]}..."

    def get_absolute_url(self):
        return reverse('prayer_marathon:detail', args=[self.id])

    class Meta:
        ordering = ('-date',)


class ShepherdReportManager(models.Manager):
    def date_series(self, shepherd=None):
        if shepherd is None:
            query = self.get_queryset()
        else:
            query = self.get_queryset().filter(receiver=shepherd)

        if query:
            female_query = query.filter(sender__gender='F')
            male_query = query.filter(sender__gender='M')

            female_object = female_query.values_list('date', flat=True)
            male_object = male_query.values_list('date', flat=True)
        else:
            return pd.to_datetime([]), pd.to_datetime([])

        return pd.to_datetime(female_object), pd.to_datetime(male_object)

    def retrieve_sheep_details_who_submit_reports(self, shepherd) -> Dict:
        """Returns the shepherd report that was sent to the shepherd"""
        
        if not isinstance(shepherd, Shepherd):
            raise TypeError("Must be a shepherd instance")
        sheep_reports = self.get_queryset().filter(receiver=shepherd)
        unique_sheep = set(sheep_reports.values_list('sender', flat=True))

        analysis = {sheep: {'full_name': None, 'no_of_reports': 0, 'no_of_missed_weeks': 0,
                            'diligence': 0}
                    for sheep in unique_sheep}

        for sheep in unique_sheep:
            reports = sheep_reports.filter(sender=sheep)
            analysis[sheep]['no_of_reports'] = len(reports)

            no_of_missed_weeks, diligence = self.missed_weeks(reports)
            analysis[sheep]['no_of_missed_weeks'] = no_of_missed_weeks
            analysis[sheep]['diligence'] = diligence
            analysis[sheep]['full_name'] = get_user_model().objects.get(id=sheep).get_full_name()

        return analysis

    def retrieve_sheep_reports_statistics(self):
        # Retrieve all the shepherd reports
        sheep_reports = self.get_queryset()

        if sheep_reports:
            # Get the primary key of each shepherd the report was sent to for each report
            shepherds = [report.receiver_id for report in sheep_reports]
            unique_shepherd = set(shepherds)

            analysis = {shepherd: {'no_of_reports': 0, 'male': 0, 'female': 0,
                                   'full_name': None}
                        for shepherd in unique_shepherd}

            # for each shepherd that has been sent a report
            for shepherd in unique_shepherd:
                # get all the reports that has been sent to this particular shepherd
                reports = sheep_reports.filter(receiver_id=shepherd)

                # get the number of females and males that has sent his/her report
                # to this particular shepherd
                male_report = len(reports.filter(sender__gender='M'))
                female_report = len(reports.filter(sender__gender='F'))

                analysis[shepherd]['no_of_reports'] = len(reports)
                analysis[shepherd]['male'] = round((male_report * 100) / len(reports))
                analysis[shepherd]['female'] = round((female_report * 100) / len(reports))
                analysis[shepherd]['full_name'] = Shepherd.objects.get(id=shepherd).name.get_full_name()
            return analysis
        else:
            return sheep_reports

    def most_diligent_sheep(self, shepherd=None):
        if shepherd is None:  # if chief shepherd return all reports
            sheep_reports = self.get_queryset().filter(date__year=timezone.now().year)
        else:  # if core shepherd returns reports sent to that particular shepherd
            if not isinstance(shepherd, Shepherd):
                raise TypeError("Must be a shepherd instance")
            sheep_reports = self.get_queryset().filter(receiver=shepherd, date__year=timezone.now().year)

        if sheep_reports:
            full_names = {report.sender.id: report.sender.get_full_name() for report in sheep_reports}
            sheep_freq = sheep_reports.values_list('sender', flat=True)
            diligent_sheep = pd.value_counts(sheep_freq).head()
        else:
            diligent_sheep, full_names = [], dict()

        return diligent_sheep, full_names

    def most_read_books(self, shepherd=None):
        if shepherd is None:
            sheep_reports = self.get_queryset()
        else:
            if not isinstance(shepherd, Shepherd):
                raise TypeError("Must be a shepherd instance")
            sheep_reports = self.get_queryset().filter(receiver=shepherd)

        if sheep_reports:
            book_freq = [report.strip().title() for report in sheep_reports.values_list('books_read', flat=True)]
            top_books = pd.value_counts(book_freq).head()
        else:
            top_books = []

        return top_books

    def overall_gender_percentage(self, shepherd=None):
        if shepherd is None:
            sheep_reports = self.get_queryset().filter(date__year=timezone.now().year)
        else:
            if not isinstance(shepherd, Shepherd):
                raise TypeError("Must be a shepherd instance")
            sheep_reports = self.get_queryset().filter(receiver=shepherd, date__year=timezone.now().year)

        if sheep_reports:
            gender = sheep_reports.values_list('sender__gender', flat=True)
            unique_gender, gender_counts = np.unique(gender, return_counts=True)
            unique_gender = unique_gender.tolist()

            total = len(gender)
            gender_percentage = [round((count * 100) / total, 1) for count in gender_counts]
        else:
            unique_gender, gender_percentage = [], 0

        return unique_gender, gender_percentage

    def missed_weeks(self, reports) -> Tuple[int, int]:
        """
        Retrieve the weeks that a sheep failed to turn in his report
        in that current year, it will resets itself every new year.
        Guys will like that feature I bet.
        """
        WEEKS_IN_A_YEAR = 52
        current_week = timezone.now().isocalendar().week
        current_year = timezone.now().year
        report_submitted_week = [item.date.isocalendar().week for item in reports
                                 if item.date.year == current_year]

        missed_weeks = current_week - len(report_submitted_week)
        diligence_percentage = (len(report_submitted_week) * 100) / WEEKS_IN_A_YEAR

        return missed_weeks, round(diligence_percentage)


class ShepherdReport(models.Model):
    # sender refers to the sheep that sent his/her shepherd report to their shepherd
    # receiver refers to the shepherds the report was sent to
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    receiver = models.ForeignKey(Shepherd, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)

    books_read = models.TextField(null=True, blank=True)
    church_work = models.TextField(null=True, blank=True)
    personal_details = models.TextField(null=True, blank=True)

    objects = models.Manager()
    shepherd_manager = ShepherdReportManager()

    def __str__(self):
        return f"Shepherd Report on {self.date.strftime('%a %d %b %Y')}"

    def get_absolute_url(self):
        return reverse('shepherd_report:detail', args=[self.id])

    class Meta:
        ordering = ('-date', )
