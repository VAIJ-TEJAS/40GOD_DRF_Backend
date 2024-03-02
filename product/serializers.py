from rest_framework import serializers
from .models import Product, Color

class ColorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    colors = ColorsSerializer(many=True, read_only=True, source='color_images')

    class Meta:
        model = Product
        fields = ['id', 'sku', 'name', 'description', 'price', 'category', 'similar_products', 'colors']
