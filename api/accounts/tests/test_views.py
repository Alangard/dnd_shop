from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from unittest.mock import patch

from ..models import Account
from ..forms import RegistrationForm

from ...store.models import Product, Variation, ProductVariations, VariationCategory, VariationValue
from ...category.models import Category
from ...carts.models import Cart, CartItem



from django.utils.translation import activate

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
# Тест 1: Status code и redirect url при успешной и безуспешного логина
# Тест 2.1: Добавление товара из анонимного режима
# Тест 2.2.: Добавление товаров в корзину для пользователя, если он добавлял товары в анонимном режиме
        

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


        self.cart = Cart.objects.create(cart_id='cart_id_123')

        self.category = Category.objects.create(category_name = 'Test category')
        self.product1 = Product.objects.create(product_name="Test1", price=120, category = self.category, slug="test1-slug")
        self.product2 = Product.objects.create(product_name="Test2", price=150, category = self.category, slug="test2-slug")
        self.variation_category_color = VariationCategory.objects.create(name="Color")
        self.variation_value_color = VariationValue.objects.create(value="Red")
        self.variation_category_size = VariationCategory.objects.create(name="Size")
        self.variation_value_size = VariationValue.objects.create(value="XS")

        self.cartItem_without_vars = CartItem.objects.create(product=self.product2, quantity = 1, cart = self.cart)
        self.cartItem_with_vars = CartItem.objects.create(product=self.product1, quantity = 1, cart = self.cart)
        self.cartItem_with_vars.variations.add(
            Variation.objects.create(variation_category=self.variation_category_color, variation_value=self.variation_value_color),
            Variation.objects.create(variation_category=self.variation_category_size, variation_value=self.variation_value_size)
        )

        



    
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
        response = client.post(login_url, {'email': 'johndoe@example.com', 'password': 'testpass123'})
        self.assertEqual(response.status_code, 302)  # Check status code
        self.assertRedirects(response, reverse('dashboard'))  # Check if the response redirects to the correct URL

        # Check failed login
        response = client.post(login_url, {'email': 'johndoe@example.com', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 302)  # Проверяем код ответа на редирект
        self.assertRedirects(response, reverse('login'))  # Check if the response redirects to the correct URL

    def test_cart_functionality_after_login(self):
        client = Client()
        login_url = reverse('login')

        response = client.post(login_url, {'email': 'johndoe@example.com', 'password': 'testpass123'})

        
        # Проверка наличия товаров в корзине пользователя после входа
        user_cart = Cart.objects.get(cart_id='cart_id_123')
        user_cart_items = CartItem.objects.filter(user = self.user)
        print(user_cart_items, user_cart)
        # self.assertEqual(user_cart_items.count(), 2)  # Учитывая добавленные товары в setUp

        # # Проверка изменения количества товаров в корзине после добавления нового товара в анонимном режиме
        # anonymous_cart = Cart.objects.create(cart_id='anonymous_cart_id')
        # CartItem.objects.create(cart=anonymous_cart, product=self.product, quantity=1)  # Добавляем товар в анонимной корзине
        # response = self.client.post(login_url, data)  # Логинимся в учетную запись

        # user_cart = Cart.objects.get(cart_id='cart_id_123')
        # user_cart_items = CartItem.objects.filter(cart=user_cart)
        # self.assertEqual(user_cart_items.count(), 3)
