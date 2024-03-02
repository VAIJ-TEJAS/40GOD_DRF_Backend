from django.contrib import admin
from .models import CartItem

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product_varient', 'quantity_display')
    list_filter = ('user', 'product_varient')
    search_fields = ('user__username', 'product_varient__color__product__sku')
    
    def quantity_display(self, obj):
        return f"{obj.quantity} pcs"
    quantity_display.short_description = "Quantity"

admin.site.register(CartItem, CartItemAdmin)
