from django.db import models
from user.models import AddressBook, User

class Shipment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey(AddressBook, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Shipment #{self.id} - {self.user.username}"
