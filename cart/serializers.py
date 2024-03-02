from inventory.models import ProductVariant
from inventory.serializers import ProductVariantSerializer
from product.models import Color
from product.serializers import ColorsSerializer, ImageSerializer, SizeSerializer
from rest_framework import serializers
from user.serializers import UserSerializer
from .models import CartItem


class CartItemProductVariantSerializer(serializers.ModelSerializer):
    color = ColorsSerializer()
    size = SizeSerializer()

    class Meta:
        model = ProductVariant
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product_varient = CartItemProductVariantSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = '__all__'

class POST_CartItemSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = '__all__'
