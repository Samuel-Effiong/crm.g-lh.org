from datetime import datetime

from django.test import TestCase
from django.utils.datastructures import MultiValueDictKeyError
from django.http.response import JsonResponse

from users.models import CustomUser
from .models import PropheticVision


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
class PropheticVisionViewTest(TestCase):
    def setUp(self) -> None:
        self.prophetic_vision_url = '/prophetic-vision/'
        self.template_name = 'dashboard/table/table-data.html'

        create_user(self, self.client)

    def test_view_loaded_correctly(self):
        response = self.client.get(self.prophetic_vision_url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template_name)

        self.assertEqual('Prayer Marathon', response.context_data['category'])

    def test_creating_prophetic_vision_with_incomplete_details(self):
        def raise_error():
            response = self.client.post(self.prophetic_vision_url, {
                'prophetic_vision_description': 'Love God with all your heart',
                'prophetic_vision_date': datetime.date().today().strftime('%m/%d/%Y'),
            })

        self.assertRaises(MultiValueDictKeyError, raise_error)

    def test_creating_propehtic_vision_with_complete_details(self):
        response = self.client.post(self.prophetic_vision_url, {
            'prophetic_vision_description': 'Love God with all your heart',
            'prophetic_vision_date': datetime.date().today().strftime('%m/%d/%Y'),
            'prophetic_vision_body': "and with all your body and soul"
        })

        self.assertEqual('Prophetic Vision', response.context_data['category'])
        self.assertEqual(200, response.status_code)

        try:
            prophetic_vision = PropheticVision.objects.get(
                description='Love God with all your heart',
                body='and with all your body and soul'
            )
        except PropheticVision.DoesNotExist:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

        self.assertContains(prophetic_vision.username, response.context_data['user'])
        user_prophetic_vision = response.context_data['lists']
        self.assertIn(prophetic_vision, user_prophetic_vision)


class PropheticVisionEditViewTest(TestCase):
    def setUp(self) -> None:
        self.template_name = 'dashboard/special-pages/detail.html'

        create_user(self, self.client)

        response = self.client.post('/prophetic-vision/', {
            'prophetic_vision_description': 'Love God with all your heart',
            'prophetic_vision_date': datetime.date().today().strftime('%m/%d/%Y'),
            'prophetic_vision_body': "and with all your body and soul"
        }, follow=True)

        if response.status_code == 200:
            prophetic_vision = PropheticVision.objects.get(
                description='Love God with all your heart',
                body='and with all your body and soul'
            )
            self.prophetic_vision_url = f"/prophetic-vision/{prophetic_vision.pk}"

    def test_prophetic_vision_update_view_is_working_correctly(self):
        response = self.client.get(self.prophetic_vision_url, follow=True)
        self.assertEqual(200, response.status_code)

        # must be an integer indicating that the primary key is the autofield
        # affliction will rise the second time
        pk = response.context_data['view'].kwargs['pk']
        self.assertIsInstance(int(pk), int)

        detail = response.context_data['object']

        self.assertEqual('Love God with all your heart', detail.description)
        self.assertEqual('and with all your body and soul', detail.body)

        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, detail.comment)
        self.assertContains(response, detail.status)

    def test_prophetic_vision_update_posting_is_working(self):
        response = self.client.post(self.prophetic_vision_url, {
            'prophetic_vision_description': 'Love God with all your heart',
            'prophetic_vision_date': datetime.date().today().strftime('%m/%d/%Y'),
            'prophetic_vision_body': "and with all your body and soul"
        })

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Love God with all your heart')

        self.assertTemplateUsed(response, self.template_name)
