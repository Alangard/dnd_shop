from django.db import models
from ..store.models import Product, VariationCategory, VariationValue

# Create your models here.

class CartItemVariations(models.Model):
    variation_category = models.ForeignKey(VariationCategory, on_delete=models.CASCADE)
    variation_value = models.ManyToManyField(VariationValue)
    is_active = models.BooleanField(default = True)
    created_date = models.DateTimeField(auto_now = True)
    

    class Meta:
        db_table = "Cart_item_variation"
        verbose_name = "CartItem variation"
        verbose_name_plural = "CartItem variations"


    def __str__(self):
        # return self.variation_category.name
        return f"v_c{self.variation_category}/v_vs{self.variation_value.values()}"

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
    variations = models.ManyToManyField(CartItemVariations, blank = True)
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
    quantity = models.IntegerField()
    is_active  = models.BooleanField(default = True)

    class Meta:
        db_table = "Cart_item"
        verbose_name = "Cart item"
        verbose_name_plural = "Cart items"

    def sub_total(self):
        return '{:.2f}'.format(self.product.price * self.quantity)

    def __unicode__(self):
        return self.product
    
