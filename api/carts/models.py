from django.db import models
from ..store.models import Product, Variation
from ..accounts.models import Account


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
    user = models.ForeignKey(Account, on_delete = models.CASCADE, null = True)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    variations = models.ManyToManyField(Variation, blank = True)
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE, null = True)
    quantity = models.IntegerField()
    is_active  = models.BooleanField(default = True)

    class Meta:
        db_table = "Cart_item"
        verbose_name = "Cart item"
        verbose_name_plural = "Cart items"

    def __unicode__(self):
        return self.product
    
