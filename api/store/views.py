from django.shortcuts import get_object_or_404, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q

from ..store.models import Product, Variation
from ..category.models import Category
from ..carts.models import CartItem

from ..carts.views import _cart_id

# Create your views here.

def store(request, category_slug = None):
    categories = None
    products = None
    products_per_page = 1

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

        variation_dict = {}
        variations = Variation.objects.filter(product=product)

        for variation in variations:
            category_name = variation.variation_category.name
            values = variation.variation_value.values() 
            value_list = [v['value'] for v in values] 
            if category_name not in variation_dict:
                variation_dict[category_name] = []
            variation_dict[category_name].extend(value_list) 


    except Exception as e:
        raise e
    
    context = {
        'product': product,
        'variation_dict': variation_dict,
        'in_cart': in_cart,
    }

    return render(request, 'store/product_detail.html', context)


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