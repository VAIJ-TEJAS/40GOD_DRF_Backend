from django.db import models
from category.models import Category

class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', blank=True,related_name='product_tags')

    def __str__(self):
        return self.name

class Color(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='color_product')
    display_name = models.CharField(max_length=100)
    color_name = models.CharField(max_length=100)
    hex_code = models.CharField(max_length=7)

    def __str__(self):
        return f"{self.product.sku} {self.product.name} {self.color_name} ({self.hex_code})"

class Image(models.Model):
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='image_color')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return str(self.image)
    
class Size(models.Model):
    text = models.CharField(max_length=100) 

    def __str__(self):
        return self.text

class Tag(models.Model):
    text = models.CharField(max_length=100) 

    def __str__(self):
        return self.text
    