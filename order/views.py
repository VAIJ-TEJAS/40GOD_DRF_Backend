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
import requests
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
        user_currency = request.query_params.get("currency", "INR").upper()

        if not cart_items.exists():
            return Response(
                {"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate total in INR
        total_inr = sum(
            item.product_varient.color.product.price * item.quantity
            for item in cart_items
        )

        conversion_rate = 1.0
        converted_total = total_inr

        # 🟩 Fetch conversion rate from Frankfurter API
        try:
            if user_currency != "INR":
                res = requests.get(
                    f"https://api.frankfurter.app/latest?from=INR&to={user_currency}",
                    timeout=5,
                )
                data = res.json()
                if "rates" in data and user_currency in data["rates"]:
                    conversion_rate = data["rates"][user_currency]
                    converted_total = float(total_inr) * float(conversion_rate)
                    print("converted_total after conversion", converted_total)
        except Exception as e:
            print("Currency conversion failed:", e)

        # Razorpay expects amount in smallest unit (e.g., cents, paise)
        order_amount = int(converted_total * 100)
        order_currency = user_currency
        order_receipt = f"receipt_{int(time.time())}"

        try:
            razorpay_order = client.order.create(
                dict(
                    amount=order_amount,
                    currency=order_currency,
                    receipt=order_receipt,
                    notes={"converted_from": "INR"},
                )
            )
        except Exception as e:
            print("Razorpay order creation failed:", e)
            return Response(
                {"error": "Razorpay order creation failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "order_id": razorpay_order["id"],
                "razorpay_key_id": os.getenv("KEY_ID"),
                "base_currency": "INR",
                "user_currency": user_currency,
                "rate": conversion_rate,
                "converted_total": round(converted_total, 2),
            },
            status=status.HTTP_200_OK,
        )
