import re
import pandas as pd
import datetime

from django.db import models
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

from .utilities import Validators, ValidationError


class OutdatedDateField(models.CharField):
    system_check_deprecated_details = {
        'msg': (
            'Date Field has been deprecated. Support for it (except '
            'in historical migrations) will be removed in a short time'
        ),
        'hint': 'Use Correct Date field instead.',  # optional
        'id': 'date.field.W900',  # pick a unique ID for your field.
    }


class CatalogManager(models.Manager):
    def total_number_of_catalog(self):
        return len(self.get_queryset())

    def retrieve_faulty_catalog(self, accept_catalog=False):
        """This refers to catalog that have missing or incorrect values in
        fields that is considered important e.g.:
        1) Date
        2) Things spoken about
        """

        query = self.get_queryset().order_by('-date')
        counts = 0

        breakdown = {'correct_date': 0, 'things_spoken_about': 0}

        faulty_catalog = []

        for catalog in query:
            if not catalog.correct_date or not catalog.things_spoken_about:
                faulty_catalog.append(catalog)
                counts += 1

            if not catalog.correct_date:
                breakdown['correct_date'] += 1
            if not catalog.things_spoken_about:
                breakdown['things_spoken_about'] += 1

        if accept_catalog:
            return counts, breakdown, faulty_catalog
        return counts, breakdown


class Catalog(models.Model):
    day = models.CharField(max_length=201, null=True, blank=True)
    date = OutdatedDateField(max_length=200, null=True, blank=True)

    help_text = """<span style="color:red;">Use this date field to record date instead of the above date field</span>"""
    correct_date = models.DateField(blank=True, null=True,
                                    validators=[Validators.validate_prevent_future_date],
                                    help_text=help_text)

    count = models.PositiveIntegerField(default=1)
    sermon_title = models.CharField(max_length=1000, null=True, blank=True)
    things_spoken_about = models.TextField()
    new_songs_received = models.TextField(null=True, blank=True)
    testimonies = models.TextField(null=True, blank=True)
    recommended_books_movies = models.TextField(null=True, blank=True)
    meta_information = models.TextField(null=True, blank=True)

    objects = models.Manager()
    catalog_manager = CatalogManager()

    class Meta:
        ordering = ('correct_date',)

    def formatted_date(self):
        if self.correct_date:
            return self.correct_date.isoformat()
        else:
            return ''

    def __str__(self):
        return f"{self.sermon_title} on {self.date}"

    @staticmethod
    def remove_nan_from_text(value):
        return value if value.strip() != 'nan' else ""

    def clean(self):
        def raise_hell(msg):
            raise ValidationError(msg)

        self.count = int(float(self.count)) if self.count != 'nan' else 1
        self.day = self.day if self.day != 'nan' else ""

        self.date = self.date if self.date != 'nan' else ""

        self.sermon_title = self.sermon_title if self.sermon_title != 'nan' else ""

        msg = "Can't be empty, discarding data"
        self.things_spoken_about = raise_hell(msg) if self.things_spoken_about == 'nan' else self.things_spoken_about if self.things_spoken_about.strip() else raise_hell(msg)

        # test if things spoken about value can be converted to integer
        # if it can, then it is a page divider, don't save it
        try:
            int(self.things_spoken_about)
        except ValueError:
            pass
        else:
            raise_hell("A page breaker line detected...ignoring")

        self.new_songs_received = self.new_songs_received if self.new_songs_received != 'nan' else ""
        self.testimonies = self.testimonies if self.testimonies != 'nan' else ""
        self.recommended_books_movies = self.recommended_books_movies if self.recommended_books_movies != 'nan' else ""

    def get_cleaned_fields_in_dict(self):
        item = {
            'count': self.count,
            'day': self.day, 'date': self.date, 'correct_date': self.correct_date, 'sermon_title': self.sermon_title,
            'things_spoken_about': self.things_spoken_about, 'testimonies': self.testimonies,
            'recommended_books_movies': self.recommended_books_movies,
            'new_songs_received': self.new_songs_received
        }

        return item


def upload_catalog_to_database(catalog_path):
    df = pd.read_csv(catalog_path)
    df = df.drop('1521', axis=1)
    df = df.astype(str)

    day_string_re = re.compile('[0-9]{1,2}[a-z]{0,3}?', re.IGNORECASE)
    day_re = re.compile("[0-9]+")
    month_re = re.compile('[A-Z]{3,15}')
    year_re = re.compile('[0-9]{4}')

    counter = 0

    for index in range(len(df)):
        row = df.iloc[index]

        date = row['DATE']

        correct_date = None
        if date and date != 'nan':
            # extract date information from string
            day, month, year = None, None, None
            try:
                day = day_string_re.search(date).group()
            except AttributeError:
                pass

            if day is not None:
                try:
                    day = day_re.search(day).group()
                except AttributeError:
                    print(date)

            if day is not None:
                try:
                    month = month_re.search(date).group().lower()

                    if 'rd' in month:
                        month = month.replace('rd', '')
                    elif 'th' in month:
                        month = month.replace('th', '')
                    elif 'nd' in month:
                        month = month.replace('nd', '')
                    elif 'st' in month:
                        month = month.replace('st', '')
                except AttributeError:
                    if 'day' in date.lower():
                        pass
                    elif date.isnumeric():
                        pass
                    pass

            if day is not None and month is not None:
                try:
                    year = year_re.search(date).group()
                except AttributeError:
                    try:
                        year = re.search("[o0-9]{4}", date, re.IGNORECASE).group()[2:]
                    except AttributeError:
                        year = datetime.date.today().strftime('%y')
                    try:
                        correct_date = datetime.datetime.strptime(f"{day} {month} {year}", "%d %B %y").date()
                    except ValueError:
                        pass

            if correct_date is None and (day is not None and month is not None and year is not None):
                try:
                    correct_date = datetime.datetime.strptime(f"{day} {month} {year}", "%d %B %Y").date()
                except ValueError:
                    if month not in ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
                                     'september', 'october', 'november', 'december']:
                        if month[:3] == 'jan':
                            month = 'january'
                        elif month[:3] == 'feb':
                            month = 'february'
                        elif month[:3] == 'mar':
                            month = 'march'
                        elif month[:3] == 'apr':
                            month = 'april'
                        elif month[:3] == 'jun':
                            month = 'june'
                        elif month[:3] == 'jul':
                            month = 'july'
                        elif month[:3] == 'aug':
                            month = 'august'
                        elif month[:3] == 'sep':
                            month = 'september'
                        elif month[:3] == 'oct':
                            month = 'october'
                        elif month[:3] == 'nov':
                            month = 'november'
                        elif month[:3] == 'dec':
                            month = 'december'

                    try:
                        correct_date = datetime.datetime.strptime(f"{day} {month} {year}", "%d %B %Y").date()
                    except ValueError:
                        pass

        catalog = Catalog(day=row['DAY'],
                          date=row['DATE'],
                          correct_date=correct_date,
                          count=row['COUNT'],
                          sermon_title=row['SERMON TITLE'],
                          things_spoken_about=row['THINGS SPOKEN ABOUT'],
                          new_songs_received=row['NEW SONGS RECEIVED'],
                          testimonies=row['TESTIMONIES'],
                          recommended_books_movies=row['RECOMMENDED BOOKS/FILMS'])

        try:
            catalog.clean()
        except ValidationError:
            continue
        else:
            counter += 1
            catalog.save()

    return counter






