from rest_framework import serializers
from .models import Order, OrderItem
from cart.serializers import CartItemSerializer  

class OrderItemSerializer(serializers.ModelSerializer):
    cart_item = CartItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'cart_item', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    order_items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')
    payment = serializers.ReadOnlyField(source='payment.id')
    shipment = serializers.ReadOnlyField(source='shipment.id')

    class Meta:
        model = Order
        fields = ['id', 'user', 'payment', 'shipment', 'date', 'total_price', 'order_items']
