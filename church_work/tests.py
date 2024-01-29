import datetime
import time

from django.test import TestCase
from django.utils.datastructures import MultiValueDictKeyError
from django.http.response import JsonResponse

from users.models import CustomUser
from .models import ChurchWork


# Create your tests here.
class ChurchWorkViewTest(TestCase):
    def setUp(self) -> None:
        self.church_work_url = '/church-work/'
        self.template_name = 'dashboard/table/table-data.html'

        self.registration_url = '/users-registration/'

        response = self.client.post(self.registration_url, {
            'first_name': 'Utibe', 'last_name': 'Ettebong',
            'username': 'Uty', 'email': 'samueleffiong@gmail.com',
            'password': 'Nkopuruk@4', 'phone_number': '09035018948',
            'address': 'Itu Road', 'occupation': 'Developer',
            'gender': 'M',
        }, follow=True)

        self.user = CustomUser.objects.get(email='samueleffiong@gmail.com')
        self.assertEqual(self.user, response.context_data['user'])

    def test_view_loaded_correctly(self):
        response = self.client.get(self.church_work_url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template_name)

        self.assertEqual('Church Work', response.context_data['category'])

        self.assertContains(response, f"Hello, {response.context_data['user'].get_full_name()}")

        # ensure the table data is empty
        self.assertContains(response, "Dedicate time to doing the work of your Father")

    def test_creating_church_work_with_incomplete_details(self):
        def raise_error():
            response = self.client.post(self.church_work_url, {
                'church_work_category': 'transcription',
                'church_work_details': "Transcribe a four hours video",
                'church_work_hours_spent': 10,
                'church_work_date': datetime.date.today()
            })

        self.assertRaises(MultiValueDictKeyError, raise_error)

    def test_creating_church_work_with_complete_details(self):
        response = self.client.post(self.church_work_url, {
            'church_work_category': 'transcription',
            'church_work_details': "Transcribe a four hours video",
            'church_work_hours_spent': 10,
            'church_work_start_time': datetime.datetime.now().time().isoformat(),
            'church_work_end_time': datetime.datetime.now().time().isoformat(),
            'church_work_date': datetime.datetime.now().strftime('%m/%d/%Y')
        }, follow=True)

        self.assertEqual('Church Work', response.context_data['category'])
        self.assertEqual(200, response.status_code)

        try:
            church_work = ChurchWork.objects.get(
                details='Transcribe a four hours video',
                date=datetime.date.today(),
                work_category='transcription'
            )
        except ChurchWork.DoesNotExist:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

        self.assertEqual(church_work.username, response.context_data['user'])
        user_church_work = response.context_data['lists']
        self.assertIn(church_work, user_church_work)


class ChurchWorkEditViewTest(TestCase):
    def setUp(self) -> None:
        self.template_name = 'dashboard/special-pages/detail.html'

        # Create a User
        self.registration_url = '/users-registration/'
        response = self.client.post(self.registration_url, {
            'first_name': 'Utibe', 'last_name': 'Ettebong',
            'username': 'Uty', 'email': 'samueleffiong@gmail.com',
            'password': 'Nkopuruk@4', 'phone_number': '09035018948',
            'address': 'Itu Road', 'occupation': 'Developer',
            'gender': 'M',
        }, follow=True)

        self.user = CustomUser.objects.get(email='samueleffiong@gmail.com')
        self.assertEqual(self.user, response.context_data['user'])

        # Create a Church work
        response = self.client.post('/church-work/', {
            'church_work_category': 'transcription',
            'church_work_details': "Transcribe a four hours video",
            'church_work_hours_spent': 10,
            'church_work_start_time': datetime.datetime.now().time().isoformat(),
            'church_work_end_time': datetime.datetime.now().time().isoformat(),
            'church_work_date': datetime.datetime.now().strftime('%m/%d/%Y')
        }, follow=True)

        if response.status_code == 200:
            church_work = ChurchWork.objects.get(
                details='Transcribe a four hours video',
                date=datetime.date.today(),
                work_category='transcription'
            )

            self.church_work_edit_url = f'/church-work/{church_work.pk}'

    def test_church_work_update_view_is_working_correctly(self):
        response = self.client.get(self.church_work_edit_url, follow=True)
        self.assertEqual(200, response.status_code)

        # must be an integer indicating that the primary key is the autofield
        # affliction will rise the second time
        pk = response.context_data['view'].kwargs['pk']
        self.assertIsInstance(int(pk), int)

        detail = response.context_data['object']

        self.assertEqual('Transcribe a four hours video', detail.details)
        self.assertContains(response, detail.details)
        self.assertContains(response, detail.work_category)
        self.assertTemplateUsed(response, self.template_name)

    def test_church_work_update_posting_is_working(self):
        data = {
            'details': "I have just been changed",
            'work_category': 'building',
            'date': '12/13/2023',
            'hours_spent': '10',
            'start_time': '13:02',
            'end_time': '17:56:00',
        }
        response = self.client.post(self.church_work_edit_url, data, follow=True)

        self.assertEqual(200, response.status_code)

        self.assertContains(response, 'Your Church Work has been successfully updated!')
        self.assertContains(response, 'I have just been changed')
        self.assertContains(response, 'building')
        self.assertTemplateUsed(response, self.template_name)
