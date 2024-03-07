from django.shortcuts import render
from django.db.models import Avg, Count
from ..store.models import Product, Feedback

# Create your views here.

def home(request):
    products = Product.objects.all().filter(is_available = True).order_by('created_date')

    for product in products:
        product.average_rating = Feedback.objects.filter(product=product, status=True).aggregate(Avg('rating'))['rating__avg']

    context = {
        'products': products,
    }
    return render(request, 'home.html', context)