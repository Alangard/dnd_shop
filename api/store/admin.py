from django.contrib import admin
from .models import Product, Variation, ProductVariations, VariationValue, VariationCategory, Feedback, ProductGallery
import admin_thumbnails


# class VariationInline(admin.TabularInline):
#     model = Variation
#     extra = 1

@admin_thumbnails.thumbnail('image') #Add preview for 'image' model field 
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'get_variations_display', 'get_price', 'stock', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'stock', 'is_active')

    def get_variations_display(self, obj):
        return ', '.join([str(variation) for variation in obj.variations.all()])
    
    def get_price(self, obj):
        return f'${obj.price}'
    
    get_variations_display.short_description = 'Variations'
    get_price.short_description = 'Price'

@admin_thumbnails.thumbnail('product_image')#Add preview for 'product_image' model field 
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'get_price', 'modified_date', 'is_available', )
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]

    def get_price(self, obj):
        return f'${obj.price}'
    get_price.short_description = 'Price'
    # inlines = [VariationInline]



admin.site.register(Product, ProductAdmin)
admin.site.register(ProductGallery)
admin.site.register(Variation)
admin.site.register(ProductVariations, ProductVariationAdmin)
admin.site.register(VariationValue)
admin.site.register(VariationCategory)
admin.site.register(Feedback)