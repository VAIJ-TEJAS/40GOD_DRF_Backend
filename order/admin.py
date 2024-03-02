from django.contrib import admin
from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date", "total_price", "payment", "shipment")
    list_filter = ("date", "user")
    search_fields = ("user__username", "id")
    date_hierarchy = "date"
    ordering = ("-date",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "cart_item", "quantity")
    list_filter = ("order", "cart_item")
    search_fields = (
        "order__id",
        "cart_item__product_varient__product__name",
        "quantity",
    )
