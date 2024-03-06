from django.contrib.auth.models import User
from django.db import models


class AddressBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="address")
    name = models.CharField(max_length=100, help_text="Name of the recipient")
    phone_number = models.CharField(
        max_length=15, help_text="Contact phone number for this address"
    )
    street_address = models.CharField(max_length=255, help_text="Street address")
    city = models.CharField(max_length=100, help_text="City")
    state = models.CharField(max_length=100, help_text="State/Province")
    postal_code = models.CharField(max_length=20, help_text="Postal/ZIP code")
    country = models.CharField(max_length=50, help_text="Country")

    def __str__(self):
        return f"{self.name}, {self.street_address}, {self.city}, {self.state}, {self.postal_code}, {self.country}"

    class Meta:
        verbose_name = "Address Book"
        verbose_name_plural = "Address Books"
