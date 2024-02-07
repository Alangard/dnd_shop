from django.test import TestCase
from ..models import Category
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os
import requests

# docker-compose run api  python manage.py test

class CategoryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        # Download and save random mock img
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_url = 'https://source.unsplash.com/random/500x400'

        response = requests.get(image_url)

        image_file = os.path.join(current_dir, 'random_image.jpg')
        with open(image_file, 'wb') as file:
            file.write(response.content)

        Category.objects.create(
            category_name='Test Category',
            slug='test-category',
            description='Test Category Description',
            category_img = SimpleUploadedFile(name='test_image.jpg', 
                                              content=open(image_file, 'rb').read())
        )

    @classmethod
    def tearDownClass(cls):
        temp_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'random_image.jpg')
        temp_image_media_path = os.path.join(settings.MEDIA_ROOT, 'photos/categories/test_image.jpg')
        if os.path.exists(temp_image_path): os.remove(temp_image_path)
        if os.path.exists(temp_image_media_path): os.remove(temp_image_media_path)


    def setUp(self):
        self.category = Category.objects.get(category_name='Test Category')

    def test_category_name_label(self):
        field_label = self.category._meta.get_field('category_name').verbose_name
        self.assertEqual(field_label, 'category name')

    def test_slug_label(self):
        field_label = self.category._meta.get_field('slug').verbose_name
        self.assertEqual(field_label, 'slug')

    def test_category_img(self):
        image_path = os.path.join(settings.MEDIA_ROOT, 'photos/categories/')
        self.assertTrue(os.path.exists(image_path))

    def test_string_representation(self):
        self.assertEqual(str(self.category), self.category.category_name)
