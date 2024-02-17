from django.db import models
from django.urls import reverse
from api.category.models import Category

# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length = 200, unique = True)
    slug = models.SlugField(max_length = 200, unique = True)
    description = models.TextField(max_length = 500, blank = True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_image = models.ImageField(upload_to = 'photos/products/')
    stock = models.PositiveIntegerField()
    is_available = models.BooleanField(default = True)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    created_date = models.DateTimeField(auto_now_add = True)
    modified_date = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = "Product"
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def get_url(self):
        return reverse('product_detail', kwargs={'category_slug': self.category.slug, 'product_slug': self.slug})

    def __str__(self):
        return self.product_name


class VariationValue(models.Model):
    value = models.CharField(max_length=200)

    class Meta:
        db_table = "Variation_value"
        verbose_name = "Variation value"
        verbose_name_plural = "Variation values"

    def __str__(self):
        return self.value


class VariationCategory(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        db_table = "Variation_category"
        verbose_name = "Variation category"
        verbose_name_plural = "Variation categories"

    def __str__(self):
        return self.name


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    variation_category = models.ForeignKey(VariationCategory, on_delete=models.CASCADE)
    variation_value = models.ManyToManyField(VariationValue)
    is_active = models.BooleanField(default = True)
    created_date = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = "Variation"
        verbose_name = "Variation"
        verbose_name_plural = "Variations"

    def __str__(self):
        # return self.variation_value
        return f"{self.product.product_name}/v_c{self.variation_category}/v_vs{self.variation_value.values()}"

    


