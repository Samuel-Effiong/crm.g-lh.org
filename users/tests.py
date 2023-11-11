import datetime
import pandas as pd

from django.contrib.auth import get_user_model, authenticate
from django.test import TestCase
from django.shortcuts import reverse
from django.core.exceptions import ValidationError

from .models import Shepherd, SubShepherd, Catalog
from .my_models.miscellaneous import upload_catalog_to_database


# Create your tests here.
def create_user(email='samueleffiong80@gmail.com', username='Senai',
                is_admin=False, **kwargs):
    User = get_user_model()

    if not is_admin:
        user = User.objects.create_user(email=email, username=username,
                                        password='Nkopuruk@4', **kwargs)
        return user
    user = User.objects.create_superuser(email=email, username=username,
                                         password='Nkopuruk@4', **kwargs)
    return user


class UsersManagersTest(TestCase):
    def test_create_user(self):
        user = create_user()
        self.assertEqual(user.email, 'samueleffiong80@gmail.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        try:
            self.assertEqual(user.username, 'Senai')
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            get_user_model().objects.create_user()
        with self.assertRaises(TypeError):
            get_user_model().objects.create_user(email="")
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email="", password="Nkopuruk@4")

    def test_create_superuser(self):
        admin_user = create_user(is_admin=True)

        self.assertEqual(admin_user.email, 'samueleffiong80@gmail.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

        try:
            self.assertEqual(admin_user.username, 'Senai')
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(email="samueleffiong80@gmail.com", password='foo',
                                                      is_superuser=False)

    def test_alternative_login_with_username(self):

        User = get_user_model()

        valid_user = create_user()

        with self.assertRaises(User.DoesNotExist):
            test_user = User.objects.get(username='senai')

        test_user = User.objects.get(username="Senai")
        self.assertEqual(valid_user, test_user)

        # check when password is True
        confirm_password = test_user.check_password("Nkopuruk@4")
        self.assertTrue(confirm_password)

        # check when password is False
        confirm_password = test_user.check_password("Nkop")
        self.assertFalse(confirm_password)

    def test_user_date_of_birth_isnt_in_the_future(self):
        dob = datetime.date.today()

        user = create_user(date_of_birth=dob)
        self.assertEqual(dob, user.date_of_birth)

        future_dob = dob + datetime.timedelta(days=1)
        with self.assertRaises(ValidationError):
            user = create_user(date_of_birth=future_dob)

    def test_ensure_a_user_shepherd_is_not_same_as_the_user(self):
        user = create_user(first_name='Michael', last_name='Peter')
        user_2 = create_user(email='love@gmail.com', username='Love',
                             first_name='Utibe', last_name='Ettebong')

        shepherd = Shepherd(name=user, no_of_sheep=5)
        shepherd.set_date_of_appointment(datetime.date.today())
        shepherd.save()

        shepherd_2 = Shepherd(name=user_2, no_of_sheep=10)
        shepherd_2.set_date_of_appointment(datetime.date.today())
        shepherd_2.save()

        # You can't be your own shepherd
        with self.assertRaises(ValidationError):
            user.set_shepherd(shepherd)

        user.set_shepherd(shepherd_2)
        self.assertNotEqual(user.shepherd.get_shepherd_full_name(), shepherd.get_shepherd_full_name(),
                            "User shepherd should not be the same as the user")

    def test_ensure_a_user_subshepherd_is_not_same_as_the_user(self):
        user = create_user(first_name='Eddidiong', last_name='Usen')
        user_2 = create_user(email='praise@gmail.com', username='Praise',
                             first_name='Praise', last_name='Godchild')

        sub_shepherd = SubShepherd(name=user, no_of_sheep=5)
        sub_shepherd.set_date_of_appointment(datetime.date.today())
        sub_shepherd.save()

        sub_shepherd_2 = SubShepherd(name=user_2, no_of_sheep=10)
        sub_shepherd_2.set_date_of_appointment(datetime.date.today())
        sub_shepherd_2.save()

        # You can't be your own sub shepherd
        with self.assertRaises(ValidationError):
            user.set_subshepherd(sub_shepherd)

        user.set_subshepherd(sub_shepherd_2)
        self.assertNotEqual(user.sub_shepherd.get_subshepherd_full_name(), sub_shepherd.get_subshepherd_full_name(),
                            "User shepherd should not be the same as the user")


class ShepherdTest(TestCase):
    def test_creation_of_shepherd(self):
        user = create_user()
        shepherd = Shepherd(name=user, no_of_sheep=5, calling='teacher')
        shepherd.set_date_of_appointment(datetime.date.today())
        shepherd.save()

        self.assertEqual(shepherd.name, user)
        self.assertEqual(shepherd.no_of_sheep, 5)
        self.assertEqual(shepherd.calling, 'teacher')
        self.assertEqual(shepherd.date_of_appointment, datetime.date.today())

    def test_date_of_appointment_isnt_in_the_future(self):
        user = create_user()
        shepherd = Shepherd(name=user)

        now = datetime.date.today()
        past = now - datetime.timedelta(days=10)
        future = now + datetime.timedelta(days=10)

        # shepherd appointment date is today
        shepherd.set_date_of_appointment(date=now)
        self.assertEqual(shepherd.date_of_appointment, now)

        # shepherd appointment date is in the past
        shepherd.set_date_of_appointment(date=past)
        self.assertEqual(shepherd.date_of_appointment, past)

        # shepherd appointment date is in the future
        with self.assertRaises(ValidationError):
            shepherd.set_date_of_appointment(date=future)

    def test_shepherd_functions(self):
        user = create_user(gender='M', first_name='Michael', last_name='Peter')
        shepherd = Shepherd(name=user, no_of_sheep=5, calling='teacher')

        date = datetime.date.today() - datetime.timedelta(5000)
        shepherd.set_date_of_appointment(date)
        shepherd.save()

        service_duration = datetime.date.today() - date
        service_year = service_duration.days // 365
        service_days = service_duration.days % 365

        service_duration = f"{service_year} year {service_days} days"
        self.assertEqual(shepherd.get_service_duration(), service_duration)

        self.assertEqual(shepherd.get_shepherd_full_name(), str(user))
        self.assertEqual(shepherd.get_shepherd_gender(), user.gender)


class SubShepherdTest(TestCase):
    def test_creation_of_sub_shepherd(self):
        user = create_user()
        sub_shepherd = SubShepherd(name=user, no_of_sheep=5, calling='teacher')
        sub_shepherd.set_date_of_appointment(datetime.date.today())
        sub_shepherd.save()

        self.assertEqual(sub_shepherd.name, user)
        self.assertEqual(sub_shepherd.no_of_sheep, 5)
        self.assertEqual(sub_shepherd.calling, 'teacher')
        self.assertEqual(sub_shepherd.date_of_appointment, datetime.date.today())

    def test_date_of_appointment_isnt_in_the_future(self):
        user = create_user()
        sub_shepherd = SubShepherd(name=user)

        now = datetime.date.today()
        past = now - datetime.timedelta(days=10)
        future = now + datetime.timedelta(days=10)

        # shepherd appointment date is today
        sub_shepherd.set_date_of_appointment(date=now)
        self.assertEqual(sub_shepherd.date_of_appointment, now)

        # shepherd appointment date is in the past
        sub_shepherd.set_date_of_appointment(date=past)
        self.assertEqual(sub_shepherd.date_of_appointment, past)

        # shepherd appointment date is in the future
        with self.assertRaises(ValidationError):
            sub_shepherd.set_date_of_appointment(date=future)

    def test_sub_shepherd_functions(self):
        user = create_user(gender='M', first_name='Michael', last_name='Peter')
        sub_shepherd = SubShepherd(name=user, no_of_sheep=5, calling='teacher')

        date = datetime.date.today() - datetime.timedelta(5000)
        sub_shepherd.set_date_of_appointment(date)
        sub_shepherd.save()

        service_duration = datetime.date.today() - date
        service_year = service_duration.days // 365
        service_days = service_duration.days % 365

        service_duration = f"{service_year} year {service_days} days"
        self.assertEqual(sub_shepherd.get_service_duration(), service_duration)

        self.assertEqual(sub_shepherd.get_subshepherd_full_name(), str(user))
        self.assertEqual(sub_shepherd.get_subshepherd_gender(), user.gender)


class CatalogTest(TestCase):
    def test_catalog_creation(self):
        catalog = Catalog.objects.create(day='Wednessday', date='able', count=2,
                                         sermon_title='love', things_spoken_about='God',
                                         testimonies='tuochi', recommended_books_movies='rick')

        self.assertEqual(catalog.day, 'Wednessday')
        self.assertEqual(catalog.date, 'able')
        self.assertEqual(catalog.count, 2)
        self.assertEqual(catalog.sermon_title, 'love')
        self.assertEqual(catalog.things_spoken_about, 'God')
        self.assertEqual(catalog.testimonies, 'tuochi')
        self.assertEqual(catalog.recommended_books_movies, 'rick')

    def test_the_clean_function(self):
        catalog = Catalog(day='Wednessday', date='2017', count=2,
                          sermon_title='love', things_spoken_about='',
                          testimonies='tuochi', recommended_books_movies='rick')

        with self.assertRaises(ValidationError):
            catalog.clean()

        catalog.things_spoken_about = 'nan'
        with self.assertRaises(ValidationError):
            catalog.clean()

        catalog.things_spoken_about = '2017'
        with self.assertRaises(ValidationError):
            catalog.clean()

        catalog.things_spoken_about = 'God'
        catalog.date = 'love'
        self.assertIsNone(catalog.clean())

    def test_uploading_to_database_using_pandas(self):

        path = 'catalog.csv'
        df = pd.read_csv(path)
        df = df.drop('1521', axis=1)
        df = df.astype(str)

        self.assertEqual(len(df), 1556)

        for index in range(len(df)):
            row = df.iloc[index]

            catalog = Catalog(day=row['DAY'], date=row['DATE'], count=row['COUNT'],
                              sermon_title=row['SERMON TITLE'],
                              things_spoken_about=row['THINGS SPOKEN ABOUT'],
                              new_songs_received=row['NEW SONGS RECEIVED'],
                              testimonies=row['TESTIMONIES'],
                              recommended_books_movies=row['RECOMMENDED BOOKS/FILMS'])

            try:
                catalog.clean()
            except ValidationError:
                with self.assertRaises(BaseException):
                    catalog.clean()

                continue
            else:
                catalog.save()

        test_upload = len(Catalog.objects.all())
        Catalog.objects.all().delete()

        upload_catalog_to_database(path)
        original_upload = len(Catalog.objects.all())

        self.assertEqual(test_upload, original_upload)

