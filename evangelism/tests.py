import datetime

from django.test import TestCase
from django.utils.datastructures import MultiValueDictKeyError
from django.http.response import JsonResponse

from users.models import CustomUser
from .models import Evangelism


# Create your tests here.
class EvangelismViewTest(TestCase):
    def setUp(self) -> None:
        self.evangelism_url = '/evangelism/'
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
        response = self.client.get(self.evangelism_url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template_name)

        self.assertEqual('Evangelism', response.context_data['category'])
        self.assertContains(response, f"Hello, {response.context_data['user'].get_full_name()}")

    def test_creating_evangelism_with_incomplete_details(self):
        def raise_error():
            response = self.client.post(self.evangelism_url, {
                'evangelism_field_of_visit': 'Itu Road',
                'evangelism_hours_spent': 2,
                'evangelism_no_led_to_christ': 10,
                'evangelism_no_of_invites': 4,
                'evangelism_follow_up': 4,
                'evangelism_no_of_invites': 4,
                'evangelism_no_baptism': 4,
                'evangelism_people_prayed': 4,
                'evangelism_prints_shared': 4,
            })

        self.assertRaises(MultiValueDictKeyError, raise_error)

    def test_creating_evangelism_with_complete_details(self):
        response = self.client.post(self.evangelism_url, {
            'evangelism_field_of_visit': 'Itu Road',
            'evangelism_hours_spent': 2,
            'evangelism_no_led_to_christ': 10,
            'evangelism_no_of_invites': 4,
            'evangelism_follow_up': 4,
            'evangelism_no_of_invites': 4,
            'evangelism_no_baptism': 4,
            'evangelism_people_prayed': 4,
            'evangelism_prints_shared': 4,
            'evangelism_snippets': 4,
            'evangelism_message_shared': 4,
            'evangelism_first_date': datetime.datetime.today(),
            'evangelism_last_date': datetime.datetime.today()
        })

        self.assertEqual('Evangelism', response.context_data['category'])
        self.assertEqual(200, response.status_code)

        try:
            evangelism = Evangelism.objects.get(
                field_of_visit='Itu Road',
                no_led_to_christ=10,
                invitees=4
            )
        except Evangelism.DoesNotExist:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

        self.assertEqual(evangelism.username, response.context_data['user'])
        user_evangelism = response.context_data['lists']
        self.assertIn(evangelism, user_evangelism)


class EvangelismEditViewTest(TestCase):
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

        # Create an evangelism report
        response = self.client.post('/evangelism/', {
            'evangelism_field_of_visit': 'Itu Road',
            'evangelism_hours_spent': 2,
            'evangelism_no_led_to_christ': 10,
            'evangelism_no_of_invites': 4,
            'evangelism_follow_up': 4,
            'evangelism_no_of_invites': 4,
            'evangelism_no_baptism': 4,
            'evangelism_people_prayed': 4,
            'evangelism_prints_shared': 4,
            'evangelism_snippets': 4,
            'evangelism_message_shared': 4,
            'evangelism_first_date': datetime.datetime.today(),
            'evangelism_last_date': datetime.datetime.today()
        }, follow=True)

        if response.status_code == 200:
            evangelism = Evangelism.objects.get(
                field_of_visit='Itu Road',
                invitees=4,
                no_led_to_christ=10
            )
            self.evangelism_url = f"/evangelism/{evangelism.pk}"

    def test_evangelism_update_view_is_working_correctly(self):
        response = self.client.get(self.evangelism_url, follow=True)
        self.assertEqual(200, response.status_code)

        # must be an integer indicating that the primary key is the autofield
        # affliction will rise the second time
        pk = response.context_data['view'].kwargs['pk']
        self.assertIsInstance(int(pk), int)

        detail = response.context_data['object']

        self.assertEqual('Itu Road', detail.field_of_visit)
        self.assertEqual(10, detail.no_led_to_christ)

        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, detail.invitees)
        self.assertContains(response, detail.holy_spirit_baptism)

    def test_church_work_update_posting_is_working(self):
        response = self.client.post(self.evangelism_url, {
            'evangelism_no_of_invites': 100,
            'evangelism_no_baptism': 1000,
            'evangelism_people_prayed': 10000,
            'evangelism_prints_shared': 100000,
        })

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 100)
        self.assertContains(response, 1000)
        self.assertContains(response, 10000)
        self.assertContains(response, 100000)
        self.assertTemplateUsed(response, self.template_name)



