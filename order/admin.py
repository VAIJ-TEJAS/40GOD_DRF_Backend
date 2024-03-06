from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline): 
    model = OrderItem
    extra = 1  
    fields = ('cart_item', 'quantity')
    readonly_fields = ('cart_item', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date", "total_price", "payment", "shipment")
    list_filter = ("date", "user")
    search_fields = ("user__username", "id")
    date_hierarchy = "date"
    ordering = ("-date",)
    inlines = [OrderItemInline] 
    readonly_fields = ('payment_details', 'shipment_details')

    def payment_details(self, instance):
        return instance.payment 

    def shipment_details(self, instance):
        return instance.shipment 

    payment_details.short_description = 'Payment Details'
    shipment_details.short_description = 'Shipment Details'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "cart_item", "quantity")
    list_filter = ("order", "cart_item")
    search_fields = (
        "order__id",
        "cart_item__product_varient__product__name",
        "quantity",
    )