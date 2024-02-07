from django.test import TestCase
from ..models import Account
from django.contrib.auth import get_user_model

# docker-compose run api  python manage.py test

class AccountModelTest(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'testpass123',
        }
     
 
    def test_create_user(self):
        User = self.user_model
        user = User.objects.create_user(**self.user_data)
 
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])
        self.assertFalse(user.is_superadmin)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_active)
        
    def test_create_superuser(self):
        User = self.user_model
        superuser = User.objects.create_superuser(**self.user_data)
 
        self.assertEqual(superuser.email, self.user_data['email'])
        self.assertEqual(superuser.username, self.user_data['username'])
        self.assertEqual(superuser.first_name, self.user_data['first_name'])
        self.assertEqual(superuser.last_name, self.user_data['last_name'])
        self.assertTrue(superuser.is_superadmin)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_active)

    def test_first_name_label(self):
        user = self.user_model.objects.create_user(**self.user_data)
        field_label = user._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')

    def test_last_name_label(self):
        user = self.user_model.objects.create_user(**self.user_data)
        field_label = user._meta.get_field('last_name').verbose_name
        self.assertEqual(field_label, 'last name')

    def test_username_max_length(self):
        user = self.user_model.objects.create_user(**self.user_data)
        max_length = user._meta.get_field('username').max_length
        self.assertEqual(max_length, 50)

    def test_email_unique(self):
        user = self.user_model.objects.create_user(**self.user_data)
        unique = user._meta.get_field('email').unique
        self.assertTrue(unique)

    def test_phone_number_unique(self):
        user = self.user_model.objects.create_user(**self.user_data)
        unique = user._meta.get_field('phone_number').unique
        self.assertTrue(unique)

   # def test_phone_number_format

    def test_str_representation(self):
        user = self.user_model.objects.create_user(**self.user_data)
        expected_str = user.email
        self.assertEqual(str(user), expected_str)

    