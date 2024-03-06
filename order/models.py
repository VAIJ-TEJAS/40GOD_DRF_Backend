from django.db import models
from cart.models import CartItem
from inventory.models import ProductVariant
from user.models import User  
from payment.models import Payment
from shipment.models import Shipment

class Order(models.Model):
    # Define choices for shipment status
    STATUS_CHOICES = [
        ('PL', 'Placed'),
        ('PR', 'Processing'),
        ('SH', 'Shipped'),
        ('DL', 'Delivered'),
        ('CA', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    shipment = models.ForeignKey(Shipment, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='PL')
    date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitem_set')
    cart_item = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.cart_item.color.product.name} in Order #{self.order.id}"
