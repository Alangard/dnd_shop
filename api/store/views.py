import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib import messages
from django.db.models import Q, Avg, Count


from .models import Product, ProductVariations, Variation, VariationCategory, VariationValue, Feedback, ProductGallery
from .forms import FeedbackForm
from ..category.models import Category
from ..carts.models import CartItem
from ..orders.models import OrderProduct

from ..carts.views import _cart_id

# Create your views here.

def store(request, category_slug = None):
    categories = None
    products = None
    products_per_page = 15

    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category = categories, is_available = True)
    else:
        products = Product.objects.all().filter(is_available = True).order_by('id')
        
    paginator = Paginator(products, products_per_page)
    page = request.GET.get('page') # get page number parameter from url
    paged_products = paginator.get_page(page)

    product_count = products.count()

    context = { 
        'products': paged_products,
        'product_count': product_count,
    }
    
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):

    try:
        product = Product.objects.get(category__slug = category_slug, slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product = product).exists()

        variations = ProductVariations.objects.filter(product=product)
        variation_dict = {}

        for variation in variations:
            for var in variation.variations.all():
                if var.variation_category.name not in variation_dict:
                    variation_dict[var.variation_category.name] = [var.variation_value.value]
                else:
                    variation_dict[var.variation_category.name].append(var.variation_value.value)

    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        try:
            order_product = OrderProduct.objects.filter(user = request.user, product_id = product.id).exists()
        except OrderProduct.DoesNotExist:
            order_product = None
    else:
        order_product = None


    # Get the feedback for product
    feedback = Feedback.objects.filter(product_id = product.id, status = True)

    # Get average reviews rating and count of reviews for product.id
    reviews = Feedback.objects.filter(product=product.id, status=True).aggregate(average = Avg('rating'), count = Count('id'))
    average_rating = float(reviews['average']) if reviews['average'] is not None else 0
    reviews_count = int(reviews['count']) if reviews['count'] is not None else 0

    # Product Gallery
    product_gallery = ProductGallery.objects.filter(product_id = product.id)

    context = {
        'product': product,
        'variation_dict': variation_dict,
        'in_cart': in_cart,
        'order_product': order_product,
        'reviews': feedback,
        'average_rating': average_rating,
        'reviews_count': reviews_count,
        'product_gallery': product_gallery,
    }

    return render(request, 'store/product_detail.html', context)


def get_product_variations_stock(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id', None)
        variations_data = data.get('data', None)

        if product_id and variations_data:
            product_variations = ProductVariations.objects.filter(product_id=product_id)

            variations = []
            for key, value in variations_data.items():
                variation_category = VariationCategory.objects.get(name=key)
                variation_value = VariationValue.objects.get(value=value)
                variation = Variation.objects.get(variation_category=variation_category, variation_value=variation_value)
                variations.append(variation)

            # Looking for a ProductVariation that includes all variations at once
            # Without this solution, it may return multiple values of one ProductVariation 
            #(occurrence due to matching with the first category and occurrence due to matching with the second category, etc).
            for variation in variations:
                product_variations = product_variations.filter(variations=variation)
            
            if product_variations.exists():
                return JsonResponse({'data': product_variations.first().stock}, status=200)
            else:
                return JsonResponse({'data': None}, status=200)

    return JsonResponse({'error': 'Invalid data'}, status=400)

def search(request):
    products = None
    product_count = 0
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains = keyword) | Q(product_name__icontains = keyword)) # get info about elasticsearch and trying it
            product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

            
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        try:
            feedback = Feedback.objects.get(user__id=request.user.id, product__id=product_id)
            form = FeedbackForm(request.POST, instance=feedback)
            message_text = 'Thank you! Your review has been updated.'
        except Feedback.DoesNotExist:
            message_text = 'Thank you! Your review has been submitted.'
            
        if form.is_valid():
            data = form.save(commit=False)
            data.ip = request.META.get('REMOTE_ADDR')
            data.product_id = product_id
            data.user_id = request.user.id
            data.save()
            
            messages.success(request, message_text)
            return redirect(url)
