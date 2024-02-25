from django.shortcuts import render, redirect
from django.http import HttpResponse
import datetime 

from .models import Order
from .forms import OrderForm
from ..carts.models import CartItem


# Create your views here.


def place_order(request, total = 0, quantity = 0):
    current_user = request.user

    #if the cart count is less then or equeal to 0, the redirect back to store
    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
            return redirect('store')
        
    total = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)
    tax = (2 * total) / 100 #2 is an example
    grand_total = total + tax
    
    if request.method == "POST":
        form = OrderForm(request.POST)
        
        if form.is_valid():
            data = form.save(commit=False)
            data.user = current_user
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get("REMOTE_ADDR")
            data.save()
            
            current_date = datetime.datetime.now().strftime("%d%m%Y")
            order_number = f"{current_date}{data.id}"
            data.order_number = order_number
            data.save()
            
            order = Order.objects.get(user = current_user, is_ordered = False, order_number = order_number)

            context = {
                 'order': order,
                 'cart_items': cart_items,
                 'total': total,
                 'tax': tax,
                 'grand_total': grand_total
            }

            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')
    

def payments(request):
    return render(request, 'orders/payments.html')