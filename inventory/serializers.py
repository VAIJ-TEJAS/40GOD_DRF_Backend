from product.serializers import SizeSerializer
from rest_framework import serializers
from .models import ProductVariant
from product.models import Color, Size


class ProductVariantColorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "display_name", "color_name", "hex_code"]


class ProductVariantSerializer(serializers.ModelSerializer):
    color = ProductVariantColorsSerializer()
    size = SizeSerializer()

    class Meta:
        model = ProductVariant
        fields = "__all__"


class SizeSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, source="product_variants")

    class Meta:
        model = Size
        fields = ["id", "text", "variants"]
