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
import razorpay


def create_order(request):
    client = razorpay.Client(auth=("YOUR_RAZORPAY_KEY", "YOUR_RAZORPAY_SECRET"))

    # Create an order
    order_amount = 5000  # Amount in paise (e.g., 5000 paise = ₹50)
    order_currency = "INR"
    order_receipt = "order_rcptid_11"
    notes = {"Shipping address": "Bommanahalli, Bangalore"}

    response = client.order.create(
        {
            "amount": order_amount,
            "currency": order_currency,
            "receipt": order_receipt,
            "notes": notes,
        }
    )

    # Return the order ID to the frontend
    return JsonResponse({"order_id": response["id"]})

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

        # Create Order
        order = Order.objects.create(
            status="PL",
            user=user,
            total_price=sum(
                item.product_varient.color.product.price * item.quantity for item in cart_items
            ), 
        )

        # Create Order Items
        for item in cart_items:
            OrderItem.objects.create(
                order=order, cart_item=item.product_varient, quantity=item.quantity
            )

        # Create Shipment
        shipment = Shipment.objects.create(
            user=user,
            address=AddressBook.objects.get(id=1),  # should be changed later to user's requested address
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
