from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from ..store.models import Product, Variation, VariationCategory, VariationValue
from .models import Cart, CartItem, CartItemVariations


# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id): 
    # Получаем продукт
    product = Product.objects.get(id=product_id)
    product_variation = []

    if request.method == 'POST':
        # Перебираем все переданные поля формы
        for item in request.POST:
            key = item
            value = request.POST[key]
            if key != 'csrfmiddlewaretoken':
                variation = None
                try:
                    variation =  CartItemVariations.objects.get(variation_category__name__iexact=key, variation_value__value__iexact=value)                    
                except:
                    variation_category = VariationCategory.objects.get(name__iexact=key)
                    variation_value = VariationValue.objects.get(value__iexact=value)
                    variation = CartItemVariations.objects.create(variation_category=variation_category)
                    variation.variation_value.add(variation_value)

                product_variation.append(variation)


    cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))
    is_cart_item_exist = CartItem.objects.filter(product=product, cart=cart).exists()

    if is_cart_item_exist:
        cart_items = CartItem.objects.filter(product=product, cart=cart)
        existing_variations_list = []
        cart_items_ids = []

        for cart_item in cart_items:
            existing_variation = cart_item.variations.all()
            existing_variations_list.append(list(existing_variation))
            cart_items_ids.append(cart_item.id)

        # Проверяем, содержится ли список выбранных Variation в списке существующих Variation
        if product_variation in existing_variations_list:
            index = existing_variations_list.index(product_variation)
            item_id = cart_items_ids[index]
            cart_item = CartItem.objects.get(product=product, id=item_id)
            cart_item.quantity += 1
            cart_item.save()
        else:
            # Создаем новую запись в CartItem с выбранными Variation
            cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
    else:
        # Создаем новую запись в CartItem с выбранными Variation
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()


    return redirect('cart')
  

def remove_cart(request, product_id, cart_item__id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product, id = product_id)

    try:
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
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product, id = product_id)
    
    try:
        cart_item = CartItem.objects.get(product = product, cart = cart, id = cart_item__id)
        cart_item.delete()
    except:
        pass
    return redirect('cart')


def cart(request, total = 0, quantity = 0, cart_items = None):
    tax = 0
    grand_total = 0 
    
    try:
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

    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total = 0, quantity = 0, cart_items = None):
    tax = 0
    grand_total = 0 
    
    try:
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