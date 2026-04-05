from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from product.models import Product, Category
from cart.models import Cart, CartItem
from order.models import Order, OrderItem
from payment.models import Payment
import json

class EcommerceIntegrationTest(TestCase):
    """F2P and P2P integration tests for the e-commerce platform"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=99.99,
            category=self.category,
            stock_quantity=10,
            seller=self.user
        )
        self.client.force_authenticate(user=self.user)
    
    def test_complete_purchase_flow(self):
        """Test complete purchase flow from product to payment (P2P)"""
        # Add product to cart
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )
        
        # Create order from cart
        order = Order.objects.create(
            user=self.user,
            total_amount=self.product.price * 2,
            shipping_address='123 Test St, Test City, TS 12345',
            status='pending'
        )
        
        # Create order items
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=self.product.price
        )
        
        # Process payment
        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            payment_method='credit_card',
            status='completed',
            transaction_id='txn_complete_flow'
        )
        
        # Verify complete flow
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(payment.status, 'completed')
    
    def test_api_endpoints_integration(self):
        """Test API endpoints integration (F2P)"""
        # Create product via API
        product_data = {
            'name': 'API Product',
            'description': 'Created via API',
            'price': '149.99',
            'category': self.category.id,
            'stock_quantity': 15
        }
        response = self.client.post('/api/products/', product_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        api_product = Product.objects.get(name='API Product')
        
        # Add to cart via API
        cart_data = {
            'product': api_product.id,
            'quantity': 3
        }
        response = self.client.post('/api/cart/add/', cart_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create order via API
        order_data = {
            'shipping_address': '456 API St, API City, AC 67890'
        }
        response = self.client.post('/api/orders/create/', order_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify order creation
        self.assertTrue(Order.objects.filter(
            user=self.user,
            shipping_address='456 API St, API City, AC 67890'
        ).exists())
