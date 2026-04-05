from django.test import TestCase
from django.contrib.auth.models import User
from django.test.utils import override_settings
from django.db import connection
from product.models import Product, Category
from cart.models import Cart, CartItem
from order.models import Order, OrderItem
import time

class PerformanceTest(TestCase):
    """Performance tests for critical operations"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
    
    @override_settings(DEBUG=True)
    def test_product_listing_performance(self):
        """Test product listing performance with large dataset"""
        # Create multiple products
        products = []
        for i in range(50):
            product = Product.objects.create(
                name=f'Product {i}',
                description=f'Description for product {i}',
                price=99.99 + i,
                category=self.category,
                stock_quantity=10 + i,
                seller=self.user
            )
            products.append(product)
        
        # Measure query performance
        start_time = time.time()
        with self.assertNumQueries(1):
            response = self.client.get('/api/products/')
        end_time = time.time()
        
        # Should respond within 1 second
        self.assertLess(end_time - start_time, 1.0)
        self.assertEqual(len(response.data), 50)
    
    def test_cart_operations_performance(self):
        """Test cart operations performance"""
        cart = Cart.objects.create(user=self.user)
        
        # Add multiple items to cart
        start_time = time.time()
        for i in range(20):
            product = Product.objects.create(
                name=f'Cart Product {i}',
                description=f'Description {i}',
                price=10.99 + i,
                category=self.category,
                stock_quantity=5,
                seller=self.user
            )
            CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=1
            )
        end_time = time.time()
        
        # Should complete within 2 seconds
        self.assertLess(end_time - start_time, 2.0)
        self.assertEqual(CartItem.objects.count(), 20)
    
    def test_order_creation_performance(self):
        """Test order creation performance"""
        # Create products for order
        products = []
        for i in range(10):
            product = Product.objects.create(
                name=f'Order Product {i}',
                description=f'Description {i}',
                price=25.99 + i,
                category=self.category,
                stock_quantity=10,
                seller=self.user
            )
            products.append(product)
        
        # Measure order creation time
        start_time = time.time()
        order = Order.objects.create(
            user=self.user,
            total_amount=sum(p.price for p in products),
            shipping_address='123 Test St, Test City, TS 12345',
            status='pending'
        )
        
        # Add order items
        for product in products:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                price=product.price
            )
        end_time = time.time()
        
        # Should complete within 1 second
        self.assertLess(end_time - start_time, 1.0)
        self.assertEqual(OrderItem.objects.filter(order=order).count(), 10)
