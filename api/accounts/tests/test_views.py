from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import activate
from django.contrib.auth.tokens import default_token_generator

from ..models import Account

from ...store.models import Product, Variation, ProductVariations, VariationCategory, VariationValue
from ...category.models import Category
from ...carts.models import Cart, CartItem
from ...carts.views import _cart_id





class RegisterTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        activate("en")
    
    def test_register_view(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': 'janedoe',
            'email': 'janedoe@example.com',
            'password': 'TestPassword1234',
            'confirm_password': 'TestPassword1234',
            'phone_number': '+1234567890',
        })

        self.assertEqual(response.status_code, 302)  # Check if the response is a redirect
        
        self.assertEqual(Account.objects.count(), 1)  # Check if an account is created
        
        user = Account.objects.first()
        self.assertEqual(user.first_name, 'Jane')  # Check user's first name
        self.assertEqual(user.last_name, 'Doe')  # Check user's last name
        self.assertEqual(user.username, 'janedoe')  # Check user's username
        self.assertEqual(user.email, 'janedoe@example.com')  # Check user's email
        self.assertEqual(user.phone_number, '+1234567890')  # Check user's phone number
        
        self.assertEqual(len(mail.outbox), 1)  # Check if one email was sent
        
        self.assertRedirects(response, '/accounts/login/?command=verification&email=janedoe@example.com/')  # Check if the response redirects to the correct URL
        

class LoginTestCase(TestCase):
    
    def setUp(self):
        self.user_model = get_user_model() 
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'testpass123',
        }
        self.user =  self.user_model.objects.create_user(**self.user_data)
        self.user.is_active = True
        self.user.save()

    def test_login_redirect(self):
        client = Client()
        login_url = reverse('login') 

        # # # Create fake request with POST data for auth and with HTTP_REFERER to redirect user to next url
        # client = Client()

        # response = client.post(
        #     login_url,
        #     {'email': 'johndoe@example.com', 'password': 'testpass123'},
        #     HTTP_REFERER = '/?next=/cart/checkout/'
        # )
        # self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, reverse('checkout'))

        # Check success login
        response = self.client.post(login_url, {'email': 'johndoe@example.com', 'password': 'testpass123'})
        self.assertEqual(response.status_code, 302)  # Check status code
        self.assertRedirects(response, reverse('dashboard'))  # Check if the response redirects to the correct URL

        # Check failed login
        response = self.client.post(login_url, {'email': 'johndoe@example.com', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 302)  # Проверяем код ответа на редирект
        self.assertRedirects(response, reverse('login'))  # Check if the response redirects to the correct URL

    # def test_cart_functionality_after_login(self):
    #     client = Client()
    #     login_url = reverse('login')

    #     # Создаем сессию и устанавливаем значение session_key

        
    #     session = self.client.session
    #     session["session_key"] = 'my_session_key'
    #     session["my_value"] = 'my_session_key'
    #     # session.session_key = 'my_session_key'
    #     session.save()

    #     session_cookie_name = settings.SESSION_COOKIE_NAME
    #     self.client.cookies[session_cookie_name] = session.session_key

    #     cart = Cart.objects.create(cart_id='my_session_key')

    #     category = Category.objects.create(category_name = 'Test category')
    #     product1 = Product.objects.create(product_name="Test1", price=120, category = category, slug="test1-slug")
    #     product2 = Product.objects.create(product_name="Test2", price=150, category = category, slug="test2-slug")
    #     variation_category_color = VariationCategory.objects.create(name="Color")
    #     variation_value_color = VariationValue.objects.create(value="Red")
    #     variation_category_size = VariationCategory.objects.create(name="Size")
    #     variation_value_size = VariationValue.objects.create(value="XS")

    #     cartItem_without_vars = CartItem.objects.create(product=product2, quantity = 1, cart = cart)
    #     cartItem_with_vars = CartItem.objects.create(product=product1, quantity = 1, cart = cart)
    #     cartItem_with_vars.variations.add(
    #         Variation.objects.create(variation_category=variation_category_color, variation_value=variation_value_color),
    #         Variation.objects.create(variation_category=variation_category_size, variation_value=variation_value_size)
    #     )
    
    #     cart = Cart.objects.get(cart_id = 'my_session_key')
    #     cart_item1 = CartItem.objects.filter(cart = cart)

    #     response = client.post(login_url, {'email': 'johndoe@example.com', 'password': 'testpass123'})

    #     print(response.wsgi_request.session.session_key, 'my_session_key')
    #     cart_item2 = CartItem.objects.filter(user = self.user)

    #     # for item in CartItem.objects.all():
    #         # print(item, item.user)

    #     # print(cart_id,cart_item1, cart_item2)

        
    #     # self.assertEqual(user_cart_items.count(), 2)  # Учитывая добавленные товары в setUp

    #     # # Проверка изменения количества товаров в корзине после добавления нового товара в анонимном режиме
    #     # anonymous_cart = Cart.objects.create(cart_id='anonymous_cart_id')
    #     # CartItem.objects.create(cart=anonymous_cart, product=self.product, quantity=1)  # Добавляем товар в анонимной корзине
    #     # response = self.client.post(login_url, data)  # Логинимся в учетную запись

    #     # user_cart = Cart.objects.get(cart_id='cart_id_123')
    #     # user_cart_items = CartItem.objects.filter(cart=user_cart)
    #     # self.assertEqual(user_cart_items.count(), 3)


class LogoutTestCase(TestCase):
    
    def setUp(self):
        self.user_model = get_user_model() 
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'testpass123',
        }
        self.user =  self.user_model.objects.create_user(**self.user_data)
        self.user.is_active = True
        self.user.save()

    def test_logout_view(self):
        client = Client()
        
        logged_in = self.client.login(email='johndoe@example.com', password='testpass123')
        self.assertTrue(logged_in)

        response = client.get(reverse('logout'))
        self.assertNotIn('_auth_user_id', response.wsgi_request.session)

        self.assertEqual(response.status_code, 302)  # Check status code
        self.assertRedirects(response, reverse('login'))  # Check if the response redirects to the correct URL


class AccountActivationTestCase(TestCase):
    def setUp(self):
        self.user_model = get_user_model() 
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'testpass123',
        }
        self.user =  self.user_model.objects.create_user(**self.user_data)

    def test_activate_account(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        response = self.client.post(reverse('activate', kwargs={'uidb64': uidb64, 'token': token}))

        self.assertEqual(response.status_code, 302)  # Expected redirect status code
        self.assertTrue(Account.objects.get(pk=self.user.pk).is_active)  # Check if user is active
        self.assertRedirects(response, reverse('login'))  # Check if redirected to login page

    def test_activate_account_invalid_data(self):
        response = self.client.post(reverse('activate', kwargs={'uidb64': 'wrong_uid', 'token': 'wrong_token'}))
        self.assertEqual(response.status_code, 302)  # Expected redirect status code
        self.assertRedirects(response, reverse('register'))  # Check if redirected to login page


class ForgotPasswordTestCase(TestCase):
    def setUp(self):
        self.user_model = get_user_model() 
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'testpass123',
        }
        self.user =  self.user_model.objects.create_user(**self.user_data)
        self.user.is_active = True
        self.user.save()

    def test_forgotPassword_view(self):
        response = self.client.post(reverse('forgotPassword'), {'email': self.user_data['email']})

        # Check sent mail
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user_data['email'], mail.outbox[0].to)

        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, reverse('login'))

    def test_forgotPassword_view_invalid_email(self):
        response = self.client.post(reverse('forgotPassword'), {'email': 'invalid@example.com'})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('forgotPassword'))


class ResetPasswordValidateTestCase(TestCase):
    def setUp(self):
        self.user_model = get_user_model() 
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'testpass123',
        }
        self.user =  self.user_model.objects.create_user(**self.user_data)
        self.user.is_active = True
        self.user.save()

        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)

    def test_resetPasswordValidate_valid_token(self):
        response = self.client.get(reverse('reset_password__validate', args=[self.uidb64, self.token]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.wsgi_request.session['uid'], str(self.user.pk))
        self.assertRedirects(response, reverse('resetPassword'))

    def test_resetPasswordValidate_invalid_token(self):
        invalid_token = 'invalidtoken'
        response = self.client.get(reverse('reset_password__validate', args=[self.uidb64, invalid_token]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


class ResetPasswordTestCase(TestCase):
    def setUp(self):
        self.user_model = get_user_model() 
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'testpass123',
        }
        self.user =  self.user_model.objects.create_user(**self.user_data)
        self.user.is_active = True
        self.user.save()

        self.client.login(email='johndoe@example.com', password='testpass123')

    def test_resetPassword_matching_passwords(self):
        session = self.client.session
        session['uid'] = self.user.pk
        session.save()

        response = self.client.post(reverse('resetPassword'), {'password': 'newpassword','confirm_password': 'newpassword'})

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword'))
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, reverse('login'))

    def test_resetPassword_non_matching_passwords(self):
        response = self.client.post(reverse('resetPassword'), {'password': 'new_password1','confirm_password': 'new_password2'})

        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('new_password1'))
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, reverse('resetPassword'))