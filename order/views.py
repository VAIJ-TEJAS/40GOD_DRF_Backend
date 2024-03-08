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
import os

client = razorpay.Client(auth=(os.getenv("KEY_ID"), os.getenv("KEY_SECRET")))

@csrf_exempt
def create_order(request):
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

@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        # Extract the payment details from request
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        
        # Setup data for signature verification
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        # Verify the payment signature
        try:
            client.utility.verify_payment_signature(params_dict)
            # If verification is successful, you can mark the payment as successful in your database
            # Update your order model accordingly
            # e.g., update_order_status(order_id, 'Paid')
            
            return JsonResponse({"status": "Payment verification successful"})
        except razorpay.errors.SignatureVerificationError:
            # If verification fails, respond accordingly
            return JsonResponse({"status": "Payment verification failed"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

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
        address_id = request.data.get('address_id')
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
