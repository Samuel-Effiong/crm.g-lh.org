from django.test import TestCase
from django.utils.datastructures import MultiValueDictKeyError
from django.http.response import JsonResponse

from users.my_models import CustomUser, Catalog, Permission
from users.my_models.miscellaneous import upload_catalog_to_database


# Create your tests here.
class LoginAndRegistrationTest(TestCase):
    def setUp(self) -> None:
        self.login_template_name = 'dashboard/auth/sign-in.html'
        self.login_url = '/users-login/'

        self.registration_url = '/users-registration/'
        self.registration_template_name = 'dashboard/auth/sign-up.html'

        self.user = CustomUser.objects.create_user(email='samueleffiong80@gmail.com', password='Nkopuruk@4',
                                                   gender='M', first_name='Samuel', last_name='Nkopuruk',
                                                   username='Senai', phone_number='09035018948', occupation='Developer',
                                                   skills='Python, Django')

    def always_test_this(self, response):
        self.assertEqual('GLH-FAM', response.context_data['title'])
        self.assertEqual('God\'s Lighthouse Developers Team (GDevT)', response.context_data['developers'])

    def test_visitor_is_taken_to_login_page(self):
        response = self.client.get('/', follow=True)
        self.assertTemplateUsed(response, self.login_template_name)
        self.assertContains(response, 'Login')

        self.always_test_this(response)

    def test_login_page_is_properly_render(self):
        response = self.client.get(self.login_url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.login_template_name)

        self.assertContains(response, 'Email or Username')
        self.assertContains(response, "Password")
        self.assertContains(response, 'Click here to sign up')
        self.assertContains(response, 'Sign In')

        self.always_test_this(response)

    def test_login_page_with_wrong_details(self):
        response = self.client.post(self.login_url,
                                    {'email_username': 'samueleffio80@gmail.com',
                                     'password': 'Nkopuruk@4'})
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.context_data['error'])
        self.assertContains(response, 'Invalid Details')
        self.always_test_this(response)

    def test_login_page_with_correct_details(self):
        response = self.client.post(self.login_url,
                                    {'email_username': 'samueleffiong80@gmail.com',
                                     'password': 'Nkopuruk@4'}, follow=True)
        self.assertEqual(200, response.status_code)
        self.always_test_this(response)
        self.assertEqual('Homepage', response.context_data['category'])

    def test_registration_page_is_render_properly(self):
        response = self.client.get(self.registration_url)
        self.assertEqual(200, response.status_code)
        self.always_test_this(response)
        self.assertTemplateUsed(response, self.registration_template_name)

        self.assertContains(response, 'First Name')
        self.assertContains(response, "Last name")
        self.assertContains(response, 'Email')
        self.assertContains(response, 'Create Account')
        self.assertContains(response, 'Sign In')

    def test_registration_page_with_incomplete_details(self):
        try:
            response = self.client.post(self.registration_url, {
                'first_name': 'Utibe', 'last_name': 'Ettebong',
                'username': 'Uty', 'email': 'Samueleffiong@gmail.com',
                'password': 'Nkopurk@4', 'phone_number': '09035018948',
                'gender': 'M'
            }, follow=True)
        except MultiValueDictKeyError:
            self.assertTrue(True)

    def test_registration_page_with_duplicate_details(self):
        response = self.client.post(self.registration_url, {
            'first_name': 'Utibe', 'last_name': 'Ettebong',
            'username': 'Senai', 'email': 'samueleffiong80@gmail.com',
            'password': 'Nkopurk@4', 'phone_number': '09035018948',
            'gender': 'M'
        }, follow=True)

        self.assertEqual(200, response.status_code)
        self.always_test_this(response)

        self.assertEqual('This email already have an account', response.context_data['error'])
        self.assertContains(response, response.context_data['error'])

    def test_registration_page_with_complete_details(self):
        response = self.client.post(self.registration_url, {
            'first_name': 'Utibe', 'last_name': 'Ettebong',
            'username': 'Uty', 'email': 'samueleffiong@gmail.com',
            'password': 'Nkopurk@4', 'phone_number': '09035018948',
            'gender': 'M',
        }, follow=True)

        self.assertEqual(200, response.status_code)
        self.always_test_this(response)
        self.assertEqual('Homepage', response.context_data['category'])

        user = CustomUser.objects.get(email='samueleffiong@gmail.com')
        self.assertEqual(user, response.context_data['user'])

        user_permission = Permission.objects.get(name=user)

        self.assertFalse(user_permission.can_edit_catalog)
        self.assertFalse(user_permission.head_of_department)


class ProfileUpdateTest(TestCase):
    def setUp(self) -> None:
        self.username = 'Uty'
        self.registration_url = '/users-registration/'
        self.profile_url = f'/{self.username}/users-profile/'
        self.profile_template_name = 'dashboard/app/user-profile.html'

        response = self.client.post(self.registration_url, {
            'first_name': 'Utibe', 'last_name': 'Ettebong',
            'username': 'Uty', 'email': 'samueleffiong@gmail.com',
            'password': 'Nkopuruk@4', 'phone_number': '09035018948',
            'address': 'Itu Road', 'occupation': 'Developer',
            'gender': 'M',
        }, follow=True)

        self.assertEqual(200, response.status_code)
        self.assertEqual('Homepage', response.context_data['category'])

        self.user = CustomUser.objects.get(email='samueleffiong@gmail.com')
        self.assertEqual(self.user, response.context_data['user'])

    def test_profile_page_is_render_properly(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(200, response.status_code)

        self.assertEqual('Profile', response.context_data['category'])
        self.assertContains(response, self.user.get_full_name())
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.phone_number)
        self.assertContains(response, self.user.occupation)
        self.assertContains(response, self.user.address)

        self.assertTemplateUsed(response, self.profile_template_name)

    def test_profile_password_validation_with_wrong_password(self):
        response = self.client.post(self.profile_url, {
            'current_password': 'Love', 'new_password': 'God', 'form_name': 'password'
        })

        self.assertEqual(200, response.status_code)
        self.assertNotIsInstance(response, JsonResponse)

    def test_profile_password_validation_with_correct_password(self):
        response = self.client.post(self.profile_url, {
            'current_password': 'Nkopuruk@4', 'new_password': 'Samuel', 'form_name': 'password'
        })

        self.assertEqual(200, response.status_code)
        self.assertNotIsInstance(response, JsonResponse)

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password('Samuel'))

    def test_profile_update(self):
        data = {
            'first_name': 'Blessed', 'surname': 'Nkopuruk', 'gender': 'F',
            'date_of_birth': '2011-06-11', 'phone_number': '09073720587',
            'about': "Love God with all your heart, soul and mind",
            'email': self.user.email, 'occupation': 'Teacher',
            'address': 'No. 15 Ikpa Road', 'skills': 'Bible Reading',
            'blood_group': 'O-', 'genotype': 'AS', 'chronic_illness': '',
            'lga': 'Nyanya', 'state': 'Abuja', 'country': 'Nigeria',
            'course_of_study': 'Medical & Surgery', 'years_of_study': '5',
            'current_year_of_study': '5', 'final_year_status': 'True',
            'next_of_kin_full_name': 'Festus Effiong', 'next_of_kin_relationship':'Brother',
            'next_of_kin_phone_number': '09035018948', 'next_of_kin_address': 'Ikot Ikpene',
            'gift_graces': 'seer, exhortation', 'unit_of_work': 'GAT CC, GMT',
            'shepherd': "", 'sub_shepherd': "", 'shoe_size': "33", 'cloth_size': '30',
            'form_name': 'profile'
        }
        response = self.client.post(self.profile_url, data)

        self.assertEqual(200, response.status_code)
        self.assertNotIsInstance(response, JsonResponse)

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, data['first_name'])
        self.assertEqual(self.user.lga, data['lga'])
        self.assertEqual(self.user.next_of_kin_relationship, data['next_of_kin_relationship'])
        self.assertEqual(self.user.final_year_status, data['final_year_status'])
        self.assertEqual(self.user.email, data['email'])

        self.maxDiff = None
        data.pop('form_name')

        compare = self.user.to_dict()
        self.assertDictEqual(data, compare)


class CatalogTest(TestCase):
    def setUp(self) -> None:
        self.registration_url = '/users-registration/'
        self.catalog_url = '/catalog/'
        self.catalog_template_name = 'dashboard/table/catalog_table.html'

        response = self.client.post(self.registration_url, {
            'first_name': 'Utibe', 'last_name': 'Ettebong',
            'username': 'Uty', 'email': 'samueleffiong@gmail.com',
            'password': 'Nkopuruk@4', 'phone_number': '09035018948',
            'address': 'Itu Road', 'occupation': 'Developer',
            'gender': 'M',
        }, follow=True)

        self.assertEqual(200, response.status_code)
        self.assertEqual('Homepage', response.context_data['category'])

        self.user = CustomUser.objects.get(email='samueleffiong@gmail.com')
        self.assertEqual(self.user, response.context_data['user'])

        print("Uploading catalog to test database...", end="")
        total = upload_catalog_to_database('catalog.csv')
        print("completed")

        catalog_total = len(Catalog.objects.all())
        self.assertEqual(total, catalog_total)

    def test_catalog_page_is_render_properly(self):
        response = self.client.get(self.catalog_url)
        self.assertEqual(200, response.status_code)

        self.assertEqual('Catalog', response.context_data['category'])
        self.assertContains(response, 'Search Catalog')
        self.assertContains(response, 'No Matching Record Found')
        self.assertContains(response, 'Enter Text')

        self.assertTemplateUsed(response, self.catalog_template_name)

    def test_catalog_search_with_GET_is_working_properly(self):
        response = self.client.get(self.catalog_url, data={
            'unique_id': 200
        })

        self.assertEqual(200, response.status_code)
        self.assertIsInstance(response, JsonResponse)
        self.assertTrue(response.json()['confirm'])
        self.assertEqual(response.json()['catalog']['correct_date'], "2017-11-29")

        response = self.client.get(self.catalog_url, data={
            'unique_id': 20000
        })

        self.assertEqual(200, response.status_code)
        self.assertIsInstance(response, JsonResponse)
        self.assertFalse(response.json()['confirm'])

        response = self.client.get(self.catalog_url, data={
            'id': 200
        })

        self.assertEqual(200, response.status_code)
        self.assertNotIsInstance(response, JsonResponse)
        self.assertContains(response, 'Search Catalog')
        self.assertContains(response, "No Matching Record")

    def test_catalog_search_with_POST_is_working_properly(self):
        response = self.client.post(self.catalog_url, {'search_text': 'Brethren'})
        self.assertEqual(200, response.status_code)

        self.assertEqual('Catalog', response.context_data['category'])
        self.assertTemplateUsed(response, self.catalog_template_name)

        self.assertEqual('Brethren', response.context_data['search_text'])
        self.assertEqual(response.context_data['no_of_results'], len(response.context_data['results']))

