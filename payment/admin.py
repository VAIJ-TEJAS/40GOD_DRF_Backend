from django.contrib import admin
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'method', 'amount')
    list_filter = ('method', 'date')
    search_fields = ('user__username', 'method')
    date_hierarchy = 'date'
    ordering = ('-date',)

admin.site.register(Payment, PaymentAdmin)
