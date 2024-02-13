from django.db import models
from ..store.models import Product

# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length = 250, blank = True)
    date_added = models.DateField(auto_now_add = True)

    class Meta:
        db_table = "Cart"
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return self.cart_id
    

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
    quantity = models.IntegerField()
    is_active  = models.BooleanField(default = True)

    class Meta:
        db_table = "Cart_item"
        verbose_name = "Cart item"
        verbose_name_plural = "Cart items"

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.product_name 
