from rest_framework import serializers
from .models import Image, Product, Color, Size, Tag


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ["id", "text"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "text"]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["id", "image"]


class ColorsSerializer(serializers.ModelSerializer):
    image_product = ImageSerializer(many=True, read_only=True, source='image_color')

    class Meta:
        model = Color
        fields = ["id", "display_name", "color_name", "hex_code", "image_product"]


class ProductSerializer(serializers.ModelSerializer):
    colors = ColorsSerializer(many=True, read_only=True, source='color_product')
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "name",
            "description",
            "price",
            "category",
            "similar_products",
            "colors",
            "tags"
        ]
