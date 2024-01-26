from django.db import models
from category.models import Category


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    similar_products = models.ManyToManyField('self', blank=True)
    color = models.CharField(max_length=50, blank=True)
    images = models.ManyToManyField('Image', blank=True,related_name='product_images')

    def __str__(self):
        return self.name


class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='image_product')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return str(self.image)