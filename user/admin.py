from django.contrib import admin
from .models import AddressBook

@admin.register(AddressBook)
class AddressBookAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'city', 'state', 'postal_code', 'country')
    list_filter = ('country', 'state', 'city')
    search_fields = ('name', 'street_address', 'city', 'postal_code', 'country', 'user__username')
