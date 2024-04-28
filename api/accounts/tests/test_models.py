from django.test import TestCase
from ..models import Account, UserProfile
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
            'phone_number': '+1234567890',
        }

        self.super_user_data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': 'janedoe',
            'email': 'janedoe@example.com',
            'password': 'testpass123',
            'phone_number': 'testica'
        }

    def tearDown(self):
        User = self.user_model
        User.objects.all().delete()

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
        super_user = User.objects.create_superuser(**self.super_user_data)
 
        self.assertEqual(super_user.email, self.super_user_data['email'])
        self.assertEqual(super_user.username, self.super_user_data['username'])
        self.assertEqual(super_user.first_name, self.super_user_data['first_name'])
        self.assertEqual(super_user.last_name, self.super_user_data['last_name'])
        self.assertEqual(super_user.phone_number, self.super_user_data['phone_number'])
        self.assertTrue(super_user.is_superadmin)
        self.assertTrue(super_user.is_staff)
        self.assertTrue(super_user.is_active)

    def test_first_name_label(self):
            user = self.user_model.objects.create_superuser(**self.super_user_data)
            field_label = user._meta.get_field('first_name').verbose_name
            self.assertEqual(field_label, 'first name')

    def test_last_name_label(self):
        user = self.user_model.objects.create_superuser(**self.super_user_data)
        field_label = user._meta.get_field('last_name').verbose_name
        self.assertEqual(field_label, 'last name')

    def test_username_max_length(self):
        user = self.user_model.objects.create_superuser(**self.super_user_data)
        max_length = user._meta.get_field('username').max_length
        self.assertEqual(max_length, 50)

    def test_email_unique(self):
        user = self.user_model.objects.create_superuser(**self.super_user_data)
        unique = user._meta.get_field('email').unique
        self.assertTrue(unique)

    def test_phone_number_unique(self):
        user = self.user_model.objects.create_superuser(**self.super_user_data)
        unique = user._meta.get_field('phone_number').unique
        self.assertTrue(unique)

    # def test_phone_number_format

    def test_str_representation(self):
        user = self.user_model.objects.create_superuser(**self.super_user_data)
        expected_str = user.email
        self.assertEqual(str(user), expected_str)
