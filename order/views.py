from order.serializers import OrderSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction

from user.models import AddressBook
from .models import Order, OrderItem
from cart.models import CartItem
from shipment.models import Shipment
from payment.models import Payment
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import razorpay
import time
import os

client = razorpay.Client(auth=(os.getenv("KEY_ID"), os.getenv("KEY_SECRET")))


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def create_order(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response(
                {"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Extract address_id from the request data
        address_id = request.data.get("address_id")
        if not address_id:
            return Response(
                {"error": "Address ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch the address using the address_id
        try:
            address = AddressBook.objects.get(id=address_id, user=user)
        except AddressBook.DoesNotExist:
            return Response(
                {"error": "Address not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Create Order
        order = Order.objects.create(
            status="PL",
            user=user,
            total_price=sum(
                item.product_varient.color.product.price * item.quantity
                for item in cart_items
            ),
        )

        # Create Order Items
        for item in cart_items:
            # Decrease the ProductVariant quantity
            product_variant = item.product_varient
            product_variant.quantity -= item.quantity
            product_variant.save()
            OrderItem.objects.create(
                order=order, cart_item=product_variant, quantity=item.quantity
            )

        # Create Shipment
        shipment = Shipment.objects.create(
            user=user,
            address=address,
        )

        # Create Payment
        payment = Payment.objects.create(
            user=user,
            method="Credit Card",
            amount=order.total_price,
            data={"details": "Payment details here"},
        )

        # Link payment and shipment to order
        order.payment = payment
        order.shipment = shipment
        order.save()

        # Clear the User's Cart
        cart_items.delete()

        return Response(
            {"success": "Order created successfully."}, status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["get"])
    @transaction.atomic
    def calculate_order(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        # Calculate order amount based on cart items
        order_amount = int(
            sum(
                item.product_varient.color.product.price * item.quantity
                for item in cart_items
            )
            * 100
        )  # Convert to paise and ensure int

        order_currency = "INR"
        order_receipt = "receipt_{}".format(int(time.time()))
        notes = {}

        response = client.order.create(
            dict(
                amount=order_amount,
                currency=order_currency,
                receipt=order_receipt,
                notes=notes,
            )
        )

        return Response(
            {"order_id": response["id"], "razorpay_key_id": os.getenv("KEY_ID")}
        )
