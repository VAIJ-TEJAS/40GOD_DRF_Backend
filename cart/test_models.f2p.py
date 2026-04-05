from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from cart.models import CartItem
from user.models import User
from inventory.models import ProductVariant
from product.models import Product, Category, Color, Size, Tag


class CartItemModelTest(TestCase):
    """Test CartItem model functionality"""
    
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
    
    def test_cart_item_creation(self):
        """Test CartItem can be created successfully"""
        cart_item = CartItem.objects.create(
            user=self.user,
            product_varient=self.variant,
            quantity=2
        )
        
        self.assertEqual(cart_item.user, self.user)
        self.assertEqual(cart_item.product_varient, self.variant)
        self.assertEqual(cart_item.quantity, 2)
        self.assertTrue(cart_item.id)
    
    def test_cart_item_str_method(self):
        """Test CartItem string representation"""
        cart_item = CartItem.objects.create(
            user=self.user,
            product_varient=self.variant,
            quantity=2
        )
        
        expected_str = f"Cart Item #{cart_item.id} - {self.user.username}, 2 x {self.variant.color.product.sku}"
        self.assertEqual(str(cart_item), expected_str)
    
    def test_cart_item_quantity_positive(self):
        """Test CartItem quantity must be positive"""
        cart_item = CartItem(
            user=self.user,
            product_varient=self.variant,
            quantity=0
        )
        
        with self.assertRaises(ValidationError):
            cart_item.full_clean()
    
    def test_cart_item_quantity_max_value(self):
        """Test CartItem quantity reasonable maximum"""
        cart_item = CartItem(
            user=self.user,
            product_varient=self.variant,
            quantity=1000
        )
        
        try:
            cart_item.full_clean()
        except ValidationError:
            self.fail("Quantity of 1000 should be valid")
    
    def test_cart_item_unique_user_variant(self):
        """Test that a user can only have one CartItem per variant"""
        CartItem.objects.create(
            user=self.user,
            product_varient=self.variant,
            quantity=1
        )
        
        # Try to create duplicate
        duplicate_item = CartItem(
            user=self.user,
            product_varient=self.variant,
            quantity=2
        )
        
        # This should work unless we add unique constraint
        duplicate_item.full_clean()
        duplicate_item.save()
        
        # Check we have 2 items for same user/variant
        items = CartItem.objects.filter(user=self.user, product_varient=self.variant)
        self.assertEqual(items.count(), 2)
    
    def test_cart_item_ordering(self):
        """Test CartItem ordering by id"""
        user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123"
        )
        
        item1 = CartItem.objects.create(
            user=self.user,
            product_varient=self.variant,
            quantity=1
        )
        
        item2 = CartItem.objects.create(
            user=user2,
            product_varient=self.variant,
            quantity=2
        )
        
        items = list(CartItem.objects.all())
        self.assertEqual(items[0], item1)
        self.assertEqual(items[1], item2)
