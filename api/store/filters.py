import django_filters
from .models import Product, ProductVariations, Variation, Category

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
    


    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'category']


    @property
    def qs(self):
        queryset = super().qs
        product_variations = ProductVariations.objects.all()
        
        for key, values in self.data.items():
            if values != '-1' and 'variations_' in key:
                variation_category = '_'.join(key.split('_')[1:])
                variation_values = self.data.getlist(key)
                
                if len(variation_values) == 1:
                    product_variations = product_variations.filter(variations__variation_category__name=variation_category, variations__variation_value__value=variation_values[0])
                elif len(variation_values) > 1:
                    product_variations = product_variations.filter(variations__variation_category__name=variation_category, variations__variation_value__value__in=variation_values)
                
                variation_ids = [pv.id for pv in product_variations]
                queryset = queryset.filter(productvariations__in=variation_ids).distinct()
            # print(f'Filtered products: {[product.variations.all() for product in product_variations]}')

        return queryset
