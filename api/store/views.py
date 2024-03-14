import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.urls import reverse


from .models import Product, ProductVariations, Variation, VariationCategory, VariationValue, Feedback, ProductGallery
from .forms import FeedbackForm
from ..category.models import Category
from ..carts.models import CartItem
from ..orders.models import OrderProduct


from ..carts.views import _cart_id

# Create your views here.

def get_filter_url(request, filters={}):
    url = request.path
    query_params = request.GET.copy()
    query_params.update(filters)
    return f"{url}?{query_params.urlencode()}"

def store(request, category_slug = None):
    category = None
    products = None
    products_per_page = 1
    # products_per_page = 15

    filter_params = {}


    products = Product.objects.all().filter(is_available = True).order_by('id')
    

    if request.method == 'POST':
        product_variations = ProductVariations.objects.all()

        for key, values in request.POST.items():

            if values != '-1':
                if key == 'category':
                    category = get_object_or_404(Category, slug = values)
                    products = products.filter(category = category, is_available = True)
                    filter_params[key] = category.slug
                elif key == 'min_price':
                    products = products.filter(price__gte = values)
                    filter_params[key] = values
                elif key == 'max_price':
                    products = products.filter(price__lte = values)
                    filter_params[key] = values
                elif 'variations_' in key:
                    variation_category = '_'.join(key.split('_')[1:])
                    variation_values = request.POST.getlist(key)

                    if len(variation_values) == 1:
                        product_variations = product_variations.filter(variations__variation_category__name=variation_category, variations__variation_value__value=variation_values[0])
                    elif len(variation_values) > 1:
                        product_variations = product_variations.filter(variations__variation_category__name=variation_category, variations__variation_value__value__in=variation_values)

                    print(f'products_test: {products}')
                    variation_ids = [pv.id for pv in product_variations]
                    products = products.filter(productvariations__in=variation_ids).distinct()

                    filter_params[key.lower()] = ','.join(variation_values)
            # print(f'Filtered products: {[product.variations.all() for product in product_variations]}')

    paginator = Paginator(products, products_per_page)
    page = request.GET.get('page') # get page number parameter from url
    paged_products = paginator.get_page(page)

    product_count = products.count()

    # Get categories for the product filter list
    variations = Variation.objects.select_related('variation_category', 'variation_value')
    variation_dict = {}
    for variation in variations:
        category_name = variation.variation_category.name
        value = variation.variation_value.value

        if category_name not in variation_dict:
            variation_dict[category_name] = []

        variation_dict[category_name].append(value)

    for product in paged_products:
        average_rating = Feedback.objects.filter(product=product, status=True).aggregate(Avg('rating'))['rating__avg']
        product.average_rating = average_rating if average_rating is not None else 0
    
    filter_url = get_filter_url(request, filter_params)

    context = { 
        'products': paged_products,
        'product_count': product_count,
        'variation_dict': variation_dict,
        'filter_url': filter_url,
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


def get_product_variations_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id', None)
        variations_data = data.get('data', None)

        product = Product.objects.get(id = product_id)

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
                return JsonResponse({'data': {'stock': product_variations.first().stock, 'price': product_variations.first().price}}, status=200)
            else:
                return JsonResponse({'data': {'stock': None, 'price': product.price}}, status=200)

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
    form = FeedbackForm(request.POST)
        
    try:
        feedback = Feedback.objects.get(user_id=request.user.id, product_id=product_id)
        message_text = 'Thank you! Your review has been updated.'
    except Feedback.DoesNotExist:
        feedback = None
        message_text = 'Thank you! Your review has been submitted.'
    
    if form.is_valid():
        form_data = form.cleaned_data
        if feedback:
            for field, value in form_data.items():
                if value != '':
                    setattr(feedback, field, value)
            feedback.save()
        else:
            data = form.save(commit=False)
            data.ip = request.META.get('REMOTE_ADDR')
            data.product_id = product_id
            data.user_id = request.user.id
            data.save()

    messages.success(request, message_text)
    return redirect(url)
