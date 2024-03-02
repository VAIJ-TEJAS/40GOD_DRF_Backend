from django.db import models
from inventory.models import ProductVariant
from user.models import User


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_varient = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='product_varient')
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"Cart Item #{self.id} - {self.user.username}, {self.quantity} x {self.product_varient.color.product.sku}"
