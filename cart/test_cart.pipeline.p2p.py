from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from cart.models import CartItem
from user.models import User
from inventory.models import ProductVariant
from product.models import Product, Category, Color, Size, Tag


class CartPipelineTest(TransactionTestCase):
    """Test cart functionality end-to-end"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            sku="TEST001",
            name="Test Product",
            description="Test Description",
            price=Decimal("99.99"),
            category=self.category
        )
        self.color = Color.objects.create(
            product=self.product,
            display_name="Red",
            color_name="Red",
            hex_code="#FF0000"
        )
        self.size = Size.objects.create(text="Large")
        self.variant = ProductVariant.objects.create(
            color=self.color,
            size=self.size,
            stock_quantity=10,
            price=Decimal("99.99")
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
    
    def test_add_to_cart_workflow(self):
        """Test complete add to cart workflow"""
        # 1. User logs in
        self.client.login(username="testuser", password="testpass123")
        
        # 2. Add item to cart
        response = self.client.post('/api/cart/add/', {
            'variant_id': self.variant.id,
            'quantity': 2
        })
        
        # 3. Check item was added
        cart_item = CartItem.objects.get(user=self.user, product_varient=self.variant)
        self.assertEqual(cart_item.quantity, 2)
        
        # 4. Verify cart contents
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['quantity'], 2)
    
    def test_update_cart_quantity_workflow(self):
        """Test updating cart quantity workflow"""
        # Create initial cart item
        CartItem.objects.create(
            user=self.user,
            product_varient=self.variant,
            quantity=1
        )
        
        self.client.login(username="testuser", password="testpass123")
        
        # Update quantity
        response = self.client.put(f'/api/cart/{self.variant.id}/update/', {
            'quantity': 5
        })
        
        # Verify update
        cart_item = CartItem.objects.get(user=self.user, product_varient=self.variant)
        self.assertEqual(cart_item.quantity, 5)
    
    def test_remove_from_cart_workflow(self):
        """Test removing item from cart workflow"""
        # Create initial cart item
        CartItem.objects.create(
            user=self.user,
            product_varient=self.variant,
            quantity=2
        )
        
        self.client.login(username="testuser", password="testpass123")
        
        # Remove item
        response = self.client.delete(f'/api/cart/{self.variant.id}/remove/')
        
        # Verify removal
        with self.assertRaises(CartItem.DoesNotExist):
            CartItem.objects.get(user=self.user, product_varient=self.variant)
    
    def test_cart_clear_workflow(self):
        """Test clearing entire cart workflow"""
        # Create multiple cart items
        variant2 = ProductVariant.objects.create(
            color=self.color,
            size=self.size,
            stock_quantity=5,
            price=Decimal("49.99")
        )
        
        CartItem.objects.create(
            user=self.user,
            product_varient=self.variant,
            quantity=2
        )
        CartItem.objects.create(
            user=self.user,
            product_varient=variant2,
            quantity=1
        )
        
        self.client.login(username="testuser", password="testpass123")
        
        # Clear cart
        response = self.client.delete('/api/cart/clear/')
        
        # Verify cart is empty
        cart_items = CartItem.objects.filter(user=self.user)
        self.assertEqual(cart_items.count(), 0)
    
    def test_cart_total_calculation_workflow(self):
        """Test cart total calculation workflow"""
        # Create cart with multiple items
        variant2 = ProductVariant.objects.create(
            color=self.color,
            size=self.size,
            stock_quantity=5,
            price=Decimal("49.99")
        )
        
        CartItem.objects.create(
            user=self.user,
            product_varient=self.variant,
            quantity=2
        )
        CartItem.objects.create(
            user=self.user,
            product_varient=variant2,
            quantity=3
        )
        
        self.client.login(username="testuser", password="testpass123")
        
        # Get cart total
        response = self.client.get('/api/cart/total/')
        
        expected_total = (Decimal("99.99") * 2) + (Decimal("49.99") * 3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], expected_total)
    
    def test_cart_stock_validation_workflow(self):
        """Test cart stock validation workflow"""
        # Set variant stock to 5
        self.variant.stock_quantity = 5
        self.variant.save()
        
        self.client.login(username="testuser", password="testpass123")
        
        # Try to add more than stock
        response = self.client.post('/api/cart/add/', {
            'variant_id': self.variant.id,
            'quantity': 10
        })
        
        # Should fail or adjust quantity
        self.assertNotEqual(response.status_code, 200)
        
        # Check that quantity doesn't exceed stock
        if CartItem.objects.filter(user=self.user, product_varient=self.variant).exists():
            cart_item = CartItem.objects.get(user=self.user, product_varient=self.variant)
            self.assertLessEqual(cart_item.quantity, 5)
