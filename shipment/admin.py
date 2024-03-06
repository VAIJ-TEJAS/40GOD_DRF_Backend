from django.contrib import admin
from .models import Shipment

class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'address')
    list_filter = ('date',)
    search_fields = ('user__username', 'address__address_line1', 'address__address_line2')
    date_hierarchy = 'date'
    ordering = ('-date',)

admin.site.register(Shipment, ShipmentAdmin)
