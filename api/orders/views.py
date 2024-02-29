from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.db.models import F
import datetime 
import json


from .models import Order, Payment, OrderProduct
from ..carts.models import CartItem
from ..store.models import Product

from .forms import OrderForm



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
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body["orderID"])

    payment = Payment.objects.create(
        user=request.user,
        payment_id=body["transID"],
        payment_method=body["payment_method"],
        amount_paid=order.order_total,
        status=body['status']
    )

    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.select_related('product').filter(user=request.user)

    # Move the cart items to OrderProduct
    for item in cart_items:
        order_product = OrderProduct.objects.create(
            order=order,
            payment=payment,
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True
        )

        product_variations = item.variations.all()
        order_product.variations.set(product_variations)

        item.product.stock = F('stock') - item.quantity
        item.product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': order.full_name,
        'order': order,
    })
    to_email = order.email
    send_email = EmailMessage(mail_subject, message, to=[to_email,])
    send_email.send()

    # Send order number and trans_id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id
    }

    return JsonResponse(data)


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order=order).select_related('product')
        payment = Payment.objects.get(payment_id=transID)
        
        subtotal = sum(product.product_price * product.quantity for product in ordered_products)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }

        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')