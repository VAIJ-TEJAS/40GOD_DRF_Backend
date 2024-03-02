from django.db import models
from user.models import AddressBook, User

class Shipment(models.Model):
    # Define choices for shipment status
    STATUS_CHOICES = [
        ('PL', 'Placed'),
        ('PR', 'Processing'),
        ('SH', 'Shipped'),
        ('DL', 'Delivered'),
        ('CA', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey(AddressBook, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='PL')

    def __str__(self):
        return f"Shipment #{self.id} - {self.user.username}, {self.status()}"
