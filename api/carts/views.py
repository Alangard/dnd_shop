from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.db import models

from ..store.models import Product, Variation, VariationCategory, VariationValue
from .models import Cart, CartItem, CartItemVariations


# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            if key != 'csrfmiddlewaretoken':
                try:
                    variation = CartItemVariations.objects.get(variation_category__name__iexact=key, variation_value__value__iexact=value)
                except:
                    variation_category, created = VariationCategory.objects.get_or_create(name__iexact=key)
                    variation_value, created = VariationValue.objects.get_or_create(value__iexact=value)
                    variation = CartItemVariations.objects.create(variation_category=variation_category)
                    variation.variation_value.add(variation_value)
                product_variation.append(variation)
        
        try:
            if current_user.is_authenticated:
                cart_items = CartItem.objects.filter(product=product, user=current_user)
            else:
                cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))
                cart_items = CartItem.objects.filter(product=product, cart=cart)
            
            if product_variation:
                cart_items = cart_items.filter(variations__in=product_variation)
            else:
                cart_items = cart_items.filter(variations=None)
            
            if cart_items.exists():
                cart_items.update(quantity=models.F('quantity') + 1)
                return redirect('cart')
            else:
                new_cart_item = CartItem.objects.create(product=product, 
                                                        quantity=1, 
                                                        user=current_user if current_user.is_authenticated else None, 
                                                        cart=cart if not current_user.is_authenticated else None)
                if product_variation:
                    new_cart_item.variations.set(product_variation)
                new_cart_item.save()
                return redirect('cart')
        except:
            pass

    return redirect('cart')


def remove_cart(request, product_id, cart_item__id):
    product = get_object_or_404(Product, id = product_id)

    try:
        if request.user.is_authenticated:
                cart_item = CartItem.objects.get(product = product, user = request.user, id = cart_item__id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product = product, cart = cart, id = cart_item__id)
        
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove__cart_item(request, product_id, cart_item__id):
    product = get_object_or_404(Product, id = product_id)
    
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product = product, user = request.user, id = cart_item__id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product = product, cart = cart, id = cart_item__id)
        cart_item.delete()
    except:
        pass
    return redirect('cart')


def cart(request, total = 0, quantity = 0, cart_items = None):
    tax = 0
    grand_total = 0 
    
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user, is_active = True).order_by('-quantity')
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active = True).order_by('-quantity')

        total = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)
        tax = (2 * total) / 100 #2 is an example
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total': '{:.2f}'.format(total),
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': '{:.2f}'.format(tax),
        'grand_total': '{:.2f}'.format(grand_total),
    }

    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total = 0, quantity = 0, cart_items = None):
    tax = 0
    grand_total = 0 
    
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user, is_active = True).order_by('-quantity')
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active = True).order_by('-quantity')
            
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100 # example
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total': '{:.2f}'.format(total),
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': '{:.2f}'.format(tax),
        'grand_total': '{:.2f}'.format(grand_total),
    }
    return render(request, 'store/checkout.html', context)