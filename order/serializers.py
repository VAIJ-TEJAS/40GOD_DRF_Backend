from inventory.models import ProductVariant
from inventory.serializers import ProductVariantSerializer
from payment.serializers import PaymentSerializer
from product.serializers import ColorsSerializer, SizeSerializer
from rest_framework import serializers
from shipment.serializers import ShipmentSerializer
from .models import Order, OrderItem


class OrderProductVariantSerializer(serializers.ModelSerializer):
    color = ColorsSerializer()
    size = SizeSerializer()

    class Meta:
        model = ProductVariant
        fields = "__all__"

class OrderItemSerializer(serializers.ModelSerializer):
    cart_item = OrderProductVariantSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "cart_item", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True, source="orderitem_set")
    payment = PaymentSerializer()
    shipment = ShipmentSerializer()

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "payment",
            "shipment",
            "date",
            "total_price",
            "order_items",
        ]
