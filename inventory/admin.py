from django.contrib import admin
from .models import ProductVariant  


class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('color', 'size', 'quantity')  
    list_filter = ('color', 'size')  
    search_fields = ('color__color_name', 'size__text') 

admin.site.register(ProductVariant, ProductVariantAdmin)  
