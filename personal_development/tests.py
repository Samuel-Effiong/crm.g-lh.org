from datetime import datetime

from django.test import TestCase
from django.utils.datastructures import MultiValueDictKeyError
from django.http.response import JsonResponse

from users.models import CustomUser
from .models import BibleReading, PrayerMarathon, ShepherdReport


def create_user(test, client):
    registration_url = '/users-registration/'

    response = client.post(registration_url, {
        'first_name': 'Utibe', 'last_name': 'Ettebong',
        'username': 'Uty', 'email': 'samueleffiong@gmail.com',
        'password': 'Nkopuruk@4', 'phone_number': '09035018948',
        'address': 'Itu Road', 'occupation': 'Developer',
        'gender': 'M',
    }, follow=True)

    test.user = CustomUser.objects.get(email='samueleffiong@gmail.com')
    test.assertEqual(test.user, response.context_data['user'])


# Create your tests here.
class BibleReadingViewTest(TestCase):
    def setUp(self) -> None:
        self.bible_reading_url = '/personal-development/bible-reading/'
        self.template_name = 'dashboard/table/table-data.html'

        create_user(self, self.client)

    def test_view_loaded_correctly(self):
        response = self.client.get(self.bible_reading_url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template_name)

        self.assertEqual('Bible Reading', response.context_data['category'])

    def test_creating_bible_reading_with_incomplete_details(self):
        def raise_error():
            response = self.client.post(self.bible_reading_url, {
                'bible_passage': 'John 17',
                'bible_reading_comment': 'Love God with all your heart',
            })

        self.assertRaises(MultiValueDictKeyError, raise_error)

    def test_creating_bible_reading_with_complete_details(self):
        response = self.client.post(self.bible_reading_url, {
            'bible_passage': 'John 17',
            'bible_reading_comment': 'Love God with all your heart',
            'bible_reading_date': datetime.today(),
            'bible_reading_status': 'Not Started'
        })

        self.assertEqual('Bible Reading', response.context_data['category'])
        self.assertEqual(200, response.status_code)

        try:
            bible_reading = BibleReading.objects.get(
                bible_passage='John 17',
                status='Not Started',
                comment='Love God with all your heart'
            )
        except BibleReading.DoesNotExist:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

        self.assertContains(bible_reading.username, response.context_data['user'])
        user_bible_reading = response.context_data['lists']
        self.assertIn(bible_reading, user_bible_reading)


class BibleReadingEditViewTest(TestCase):
    def setUp(self) -> None:
        self.template_name = 'dashboard/special-pages/detail.html'

        create_user(self, self.client)

        response = self.client.post('/personal-development/bible-reading/', {
            'bible_passage': 'John 17',
            'bible_reading_comment': 'Love God with all your heart',
            'bible_reading_date': datetime.today(),
            'bible_reading_status': 'Not Started'
        }, follow=True)

        if response.status_code == 200:
            bible_reading = BibleReading.objects.get(
                bible_passage='John 17',
                status='Not Started',
                comment='Love God with all your heart'
            )
            self.bible_reading_url = f"/personal-development/bible-reading/{bible_reading.pk}"

    def test_bible_reading_update_view_is_working_correctly(self):
        response = self.client.ge(self.bible_reading_url, follow=True)
        self.assertEqual(200, response.status_code)

        # must be an integer indicating that the primary key is the autofield
        # affliction will rise the second time
        pk = response.context_data['view'].kwargs['pk']
        self.assertIsInstance(int(pk), int)

        detail = response.context_data['object']

        self.assertEqual('John 17', detail.bible_passage)
        self.assertEqual('Love God with all your heart', detail.comment)

        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, detail.bible_passage)
        self.assertContains(response, detail.comment)

    def test_bible_reading_update_posting_is_working(self):
        response = self.client.post(self.bible_reading_url, {
            'bible_passage': 'John 17',
            'bible_reading_comment': 'Love God with all your heart',
            'bible_reading_date': datetime.today(),
            'bible_reading_status': 'Not Started'
        })

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'John 17')
        self.assertContains(response, 'Love God with all your heart')

        self.assertTemplateUsed(response, self.template_name)


class PrayerMarathonViewTest(TestCase):
    def setUp(self) -> None:
        self.prayer_marathon_url = '/personal-development/prayer-marathon/'
        self.template_name = 'dashboard/table/table-data.html'

        create_user(self, self.client)

    def test_view_loaded_correctly(self):
        response = self.client.get(self.prayer_marathon_url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template_name)

        self.assertEqual('Prayer Marathon', response.context_data['category'])

    def test_creating_prayer_marathon_with_incomplete_details(self):
        def raise_error():
            response = self.client.post(self.prayer_marathon_url, {
                'comment': 'Love God with all your heart',
            })

        self.assertRaises(MultiValueDictKeyError, raise_error)

    def test_creating_prayer_marathon_with_complete_details(self):
        response = self.client.post(self.prayer_marathon_url, {
            'comment': 'Love God with all your heart',
            'date': datetime.date().today().strftime('%m/%d/%Y'),
            'status': 'Not Started'
        })

        self.assertEqual('Prayer Marathon', response.context_data['category'])
        self.assertEqual(200, response.status_code)

        try:
            prayer_marathon = PrayerMarathon.objects.get(
                status='Not Started',
                comment='Love God with all your heart'
            )
        except PrayerMarathon.DoesNotExist:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

        self.assertContains(prayer_marathon.username, response.context_data['user'])
        user_bible_reading = response.context_data['lists']
        self.assertIn(prayer_marathon, user_bible_reading)


class PrayerMarathonEditViewTest(TestCase):
    def setUp(self) -> None:
        self.template_name = 'dashboard/special-pages/detail.html'

        create_user(self, self.client)

        response = self.client.post('/personal-development/prayer-marathon/', {
            'comment': 'Love God with all your heart',
            'date': datetime.date().today().strftime('%m/%d/%Y'),
            'status': 'Not Started'
        }, follow=True)

        if response.status_code == 200:
            prayer_marathon = PrayerMarathon.objects.get(
                status='Not Started',
                comment='Love God with all your heart'
            )
            self.prayer_marathon_url = f"/personal-development/prayer-marathon/{prayer_marathon.pk}"

    def test_prayer_marathon_update_view_is_working_correctly(self):
        response = self.client.ge(self.prayer_marathon_url, follow=True)
        self.assertEqual(200, response.status_code)

        # must be an integer indicating that the primary key is the autofield
        # affliction will rise the second time
        pk = response.context_data['view'].kwargs['pk']
        self.assertIsInstance(int(pk), int)

        detail = response.context_data['object']

        self.assertEqual('Not Started', detail.status)
        self.assertEqual('Love God with all your heart', detail.comment)

        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, detail.comment)
        self.assertContains(response, detail.status)

    def test_prayer_marathon_update_posting_is_working(self):
        response = self.client.post(self.prayer_marathon_url, {
            'status':'Not Started',
            'comment':'Love God with all your heart'
        })

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Love God with all your heart')

        self.assertTemplateUsed(response, self.template_name)


class ShepherdReportViewTest(TestCase):
    def setUp(self) -> None:
        self.shepherd_report_url = '/personal-development/shepherd-report/'
        self.template_name = 'dashboard/table/table-data.html'

        create_user(self, self.client)

    def test_view_loaded_correctly(self):
        response = self.client.get(self.shepherd_report_url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template_name)

        self.assertEqual('Shepherd Report', response.context_data['category'])

    def test_creating_shepherd_report_with_incomplete_details(self):
        def raise_error():
            response = self.client.post(self.shepherd_report_url, {
                'shepherd_report_church_work': "Upgraded the website",
                'shepherd_report_personal_details': "God has saved my brother",
            })

        self.assertRaises(MultiValueDictKeyError, raise_error)

    def test_creating_shepherd_report_with_complete_details(self):
        response = self.client.post(self.shepherd_report_url, {
            'shepherd_report_church_work': "Upgraded the website",
            'shepherd_report_personal_details': "God has saved my brother",
            'shepherd_report_date': datetime.date().today().strftime('%m/%d/%Y'),
            'shepherd_report_books_read': 'This Present Darkness',
        })

        self.assertEqual('Shepherd Report', response.context_data['category'])
        self.assertEqual(200, response.status_code)

        try:
            shepherd_report = ShepherdReport.objects.get(
                church_work="Upgraded the website",
                personal_details='God has saved my brother'
            )
        except ShepherdReport.DoesNotExist:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

        self.assertContains(shepherd_report.username, response.context_data['user'])
        user_shepherd_report = response.context_data['lists']
        self.assertIn(shepherd_report, user_shepherd_report)


class ShepherdReportEditViewTest(TestCase):
    def setUp(self) -> None:
        self.template_name = 'dashboard/special-pages/detail.html'

        create_user(self, self.client)

        response = self.client.post('/personal-development/shepherd-report/', {
            'shepherd_report_church_work': "Upgraded the website",
            'shepherd_report_personal_details': "God has saved my brother",
            'shepherd_report_date': datetime.date().today().strftime('%m/%d/%Y'),
            'shepherd_report_books_read': 'This Present Darkness',
        }, follow=True)

        if response.status_code == 200:
            shepherd_report = ShepherdReport.objects.get(
                church_work="Upgraded the website",
                personal_details='God has saved my brother'
            )
            self.shepherd_report_url = f"/personal-development/shepherd-report/{shepherd_report.pk}"

    def test_shepherd_report_update_view_is_working_correctly(self):
        response = self.client.get(self.shepherd_report_url, follow=True)
        self.assertEqual(200, response.status_code)

        # must be an integer indicating that the primary key is the autofield
        # affliction will rise the second time
        pk = response.context_data['view'].kwargs['pk']
        self.assertIsInstance(int(pk), int)

        detail = response.context_data['object']

        self.assertEqual('Upgraded the website', detail.church_work)
        self.assertEqual('God has saved my brother', detail.personal_details)

        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, detail.church_work)
        self.assertContains(response, detail.books_read)

    def test_prayer_marathon_update_posting_is_working(self):
        response = self.client.post(self.shepherd_report_url, {
            'shepherd_report_church_work': "Upgraded the website",
            'shepherd_report_personal_details': "God has saved my brother",
            'shepherd_report_date': datetime.date().today().strftime('%m/%d/%Y'),
            'shepherd_report_books_read': 'This Present Darkness',
        })

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'God has saved my brother')

        self.assertTemplateUsed(response, self.template_name)


