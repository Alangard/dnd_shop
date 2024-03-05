from django.contrib import admin
from .models import Product, Variation, VariationValue, VariationCategory, Feedback
# Register your models here.

# class VariationInline(admin.TabularInline):
#     model = Variation
#     extra = 1

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'get_variation_values', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value', 'is_active')
    
    def get_variation_values(self, obj):
        return "/".join([value.value for value in obj.variation_value.all()])  
     
    get_variation_values.short_description = 'Variation Values'

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available', )
    prepopulated_fields = {'slug': ('product_name',)}
    # inlines = [VariationInline]



admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(VariationValue)
admin.site.register(VariationCategory)
admin.site.register(Feedback)