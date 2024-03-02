from django.db import models
from product.models import Color, Product, Size


class ProductVariant(models.Model):
    color = models.ForeignKey(
        Color, on_delete=models.CASCADE, related_name="product_variants"
    )
    size = models.ForeignKey(
        Size, on_delete=models.CASCADE, related_name="product_variants"
    )
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.color.color_name} - {self.size.text} - Qty: {self.quantity}"
