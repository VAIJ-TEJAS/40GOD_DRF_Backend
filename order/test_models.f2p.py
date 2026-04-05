from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime, timedelta
from order.models import Order, OrderItem
from user.models import User
from inventory.models import ProductVariant
from product.models import Product, Category, Color, Size


class OrderModelTest(TestCase):
    """Test Order model functionality"""
    
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
    
    def test_order_creation(self):
        """Test Order can be created successfully"""
        order = Order.objects.create(
            user=self.user,
            total_amount=Decimal("199.98"),
            status="pending"
        )
        
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_amount, Decimal("199.98"))
        self.assertEqual(order.status, "pending")
        self.assertTrue(order.id)
        self.assertIsNotNone(order.created_at)
    
    def test_order_str_method(self):
        """Test Order string representation"""
        order = Order.objects.create(
            user=self.user,
            total_amount=Decimal("199.98"),
            status="pending"
        )
        
        expected_str = f"Order #{order.id} - {self.user.username}"
        self.assertEqual(str(order), expected_str)
    
    def test_order_status_choices(self):
        """Test Order status field choices"""
        # Test various status values
        statuses = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]
        
        for status in statuses:
            order = Order.objects.create(
                user=self.user,
                total_amount=Decimal("99.99"),
                status=status
            )
            self.assertEqual(order.status, status)
    
    def test_order_total_calculation(self):
        """Test Order total amount calculation"""
        # Create order with multiple items
        order = Order.objects.create(
            user=self.user,
            total_amount=Decimal("0.00"),
            status="pending"
        )
        
        # Add order items
        OrderItem.objects.create(
            order=order,
            product_variant=self.variant,
            quantity=2,
            price=Decimal("99.99")
        )
        
        # Calculate expected total
        expected_total = Decimal("99.99") * 2
        order.total_amount = expected_total
        order.save()
        
        # Verify total
        saved_order = Order.objects.get(id=order.id)
        self.assertEqual(saved_order.total_amount, expected_total)
    
    def test_order_user_relationship(self):
        """Test Order-User relationship"""
        order = Order.objects.create(
            user=self.user,
            total_amount=Decimal("99.99"),
            status="pending"
        )
        
        # Test forward relationship
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.user.username, "testuser")
        
        # Test reverse relationship
        user_orders = Order.objects.filter(user=self.user)
        self.assertEqual(user_orders.count(), 1)
        self.assertIn(order, user_orders)


class OrderItemModelTest(TestCase):
    """Test OrderItem model functionality"""
    
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
        self.order = Order.objects.create(
            user=self.user,
            total_amount=Decimal("0.00"),
            status="pending"
        )
    
    def test_order_item_creation(self):
        """Test OrderItem can be created successfully"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product_variant=self.variant,
            quantity=2,
            price=Decimal("99.99")
        )
        
        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.product_variant, self.variant)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, Decimal("99.99"))
        self.assertTrue(order_item.id)
    
    def test_order_item_str_method(self):
        """Test OrderItem string representation"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product_variant=self.variant,
            quantity=2,
            price=Decimal("99.99")
        )
        
        expected_str = f"OrderItem #{order_item.id} - {self.variant.color.product.name} (x{order_item.quantity})"
        self.assertEqual(str(order_item), expected_str)
    
    def test_order_item_quantity_validation(self):
        """Test OrderItem quantity validation"""
        # Test positive quantity
        order_item = OrderItem.objects.create(
            order=self.order,
            product_variant=self.variant,
            quantity=1,
            price=Decimal("99.99")
        )
        self.assertEqual(order_item.quantity, 1)
        
        # Test zero quantity (should be allowed unless constrained)
        order_item.quantity = 0
        order_item.save()
        
        saved_item = OrderItem.objects.get(id=order_item.id)
        self.assertEqual(saved_item.quantity, 0)
        
        # Test negative quantity (should be allowed unless constrained)
        order_item.quantity = -1
        order_item.save()
        
        saved_item = OrderItem.objects.get(id=order_item.id)
        self.assertEqual(saved_item.quantity, -1)
    
    def test_order_item_price_validation(self):
        """Test OrderItem price validation"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product_variant=self.variant,
            quantity=1,
            price=Decimal("99.99")
        )
        
        # Test price update
        order_item.price = Decimal("129.99")
        order_item.save()
        
        saved_item = OrderItem.objects.get(id=order_item.id)
        self.assertEqual(saved_item.price, Decimal("129.99"))
    
    def test_order_item_relationships(self):
        """Test OrderItem relationships"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product_variant=self.variant,
            quantity=2,
            price=Decimal("99.99")
        )
        
        # Test order relationship
        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.order.user, self.user)
        
        # Test product variant relationship
        self.assertEqual(order_item.product_variant, self.variant)
        self.assertEqual(order_item.product_variant.color.product, self.product)
    
    def test_order_item_total_calculation(self):
        """Test OrderItem total calculation"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product_variant=self.variant,
            quantity=3,
            price=Decimal("99.99")
        )
        
        # Calculate total
        item_total = order_item.price * order_item.quantity
        expected_total = Decimal("99.99") * 3
        
        self.assertEqual(item_total, expected_total)
    
    def test_order_orderitem_relationship(self):
        """Test Order-OrderItem relationship"""
        # Create multiple order items
        order_item1 = OrderItem.objects.create(
            order=self.order,
            product_variant=self.variant,
            quantity=1,
            price=Decimal("99.99")
        )
        
        # Create second variant
        color2 = Color.objects.create(
            product=self.product,
            display_name="Blue",
            color_name="Blue",
            hex_code="#0000FF"
        )
        variant2 = ProductVariant.objects.create(
            color=color2,
            size=self.size,
            stock_quantity=5,
            price=Decimal("89.99")
        )
        
        order_item2 = OrderItem.objects.create(
            order=self.order,
            product_variant=variant2,
            quantity=2,
            price=Decimal("89.99")
        )
        
        # Test order items relationship
        order_items = self.order.orderitem_set.all()
        self.assertEqual(order_items.count(), 2)
        self.assertIn(order_item1, order_items)
        self.assertIn(order_item2, order_items)
        
        # Test order total calculation
        total = sum(item.price * item.quantity for item in order_items)
        expected_total = (Decimal("99.99") * 1) + (Decimal("89.99") * 2)
        self.assertEqual(total, expected_total)
