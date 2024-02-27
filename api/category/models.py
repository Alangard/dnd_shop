from django.db import models
from django.urls import reverse


# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length = 50, unique = True)
    slug = models.SlugField(max_length = 100, unique = True)
    description = models.CharField(max_length = 255, blank = True)
    category_img = models.ImageField(upload_to = 'photos/categories/', blank = True)

    class Meta:
        db_table = "Category"
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def get_url(self):
        return reverse('products_by_category', kwargs={'category_slug': self.slug})
  
    def __str__(self):
        return self.category_name
    
    