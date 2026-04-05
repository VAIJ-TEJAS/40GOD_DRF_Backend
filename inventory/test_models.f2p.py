from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from inventory.models import ProductVariant
from product.models import Product, Category, Color, Size


class ProductVariantModelTest(TestCase):
    """Test ProductVariant model functionality"""
    
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
    
    def test_product_variant_creation(self):
        """Test ProductVariant can be created successfully"""
        variant = ProductVariant.objects.create(
            color=self.color,
            size=self.size,
            stock_quantity=10,
            price=Decimal("99.99")
        )
        
        self.assertEqual(variant.color, self.color)
        self.assertEqual(variant.size, self.size)
        self.assertEqual(variant.stock_quantity, 10)
        self.assertEqual(variant.price, Decimal("99.99"))
        self.assertTrue(variant.id)
    
    def test_product_variant_str_method(self):
        """Test ProductVariant string representation"""
        variant = ProductVariant.objects.create(
            color=self.color,
            size=self.size,
            stock_quantity=10,
            price=Decimal("99.99")
        )
        
        expected_str = f"{variant.color.product.name} - {variant.color.display_name} - {variant.size.text}"
        self.assertEqual(str(variant), expected_str)
    
    def test_product_variant_stock_validation(self):
        """Test ProductVariant stock quantity validation"""
        # Test positive stock
        variant = ProductVariant.objects.create(
            color=self.color,
            size=self.size,
            stock_quantity=0,
            price=Decimal("99.99")
        )
        self.assertEqual(variant.stock_quantity, 0)
        
        # Test negative stock (should be allowed unless constrained)
        variant.stock_quantity = -5
        variant.save()
        
        saved_variant = ProductVariant.objects.get(id=variant.id)
        self.assertEqual(saved_variant.stock_quantity, -5)
    
    def test_product_variant_price_validation(self):
        """Test ProductVariant price validation"""
        # Test positive price
        variant = ProductVariant.objects.create(
            color=self.color,
            size=self.size,
            stock_quantity=10,
            price=Decimal("99.99")
        )
        self.assertEqual(variant.price, Decimal("99.99"))
        
        # Test zero price
        variant.price = Decimal("0.00")
        variant.save()
        
        saved_variant = ProductVariant.objects.get(id=variant.id)
        self.assertEqual(saved_variant.price, Decimal("0.00"))
        
        # Test negative price (should be allowed unless constrained)
        variant.price = Decimal("-10.00")
        variant.save()
        
        saved_variant = ProductVariant.objects.get(id=variant.id)
        self.assertEqual(saved_variant.price, Decimal("-10.00"))
    
    def test_product_variant_unique_constraint(self):
        """Test ProductVariant unique constraint on color and size"""
        # Create first variant
        ProductVariant.objects.create(
            color=self.color,
            size=self.size,
            stock_quantity=10,
            price=Decimal("99.99")
        )
        
        # Try to create duplicate variant
        # This should work unless unique constraint is added
        variant2 = ProductVariant(
            color=self.color,
            size=self.size,
            stock_quantity=5,
            price=Decimal("89.99")
        )
        variant2.full_clean()
        variant2.save()
        
        # Check we have 2 variants with same color and size
        variants = ProductVariant.objects.filter(color=self.color, size=self.size)
        self.assertEqual(variants.count(), 2)
    
    def test_product_variant_relationships(self):
        """Test ProductVariant relationships with related models"""
        variant = ProductVariant.objects.create(
            color=self.color,
            size=self.size,
            stock_quantity=10,
            price=Decimal("99.99")
        )
        
        # Test color relationship
        self.assertEqual(variant.color, self.color)
        self.assertEqual(variant.color.product, self.product)
        self.assertEqual(variant.color.display_name, "Red")
        
        # Test size relationship
        self.assertEqual(variant.size, self.size)
        self.assertEqual(variant.size.text, "Large")
        
        # Test product through color
        self.assertEqual(variant.color.product, self.product)
        self.assertEqual(variant.color.product.sku, "TEST001")
    
    def test_product_variant_ordering(self):
        """Test ProductVariant ordering"""
        # Create multiple variants
        size2 = Size.objects.create(text="Medium")
        size3 = Size.objects.create(text="Small")
        
        variant1 = ProductVariant.objects.create(
            color=self.color,
            size=self.size,  # Large
            stock_quantity=10,
            price=Decimal("99.99")
        )
        variant2 = ProductVariant.objects.create(
            color=self.color,
            size=size2,  # Medium
            stock_quantity=15,
            price=Decimal("89.99")
        )
        variant3 = ProductVariant.objects.create(
            color=self.color,
            size=size3,  # Small
            stock_quantity=20,
            price=Decimal("79.99")
        )
        
        # Test default ordering (by id)
        variants = list(ProductVariant.objects.all())
        self.assertEqual(variants[0], variant1)
        self.assertEqual(variants[1], variant2)
        self.assertEqual(variants[2], variant3)
    
    def test_product_variant_stock_management(self):
        """Test ProductVariant stock management operations"""
        variant = ProductVariant.objects.create(
            color=self.color,
            size=self.size,
            stock_quantity=10,
            price=Decimal("99.99")
        )
        
        # Test initial stock
        self.assertEqual(variant.stock_quantity, 10)
        
        # Test stock increase
        variant.stock_quantity += 5
        variant.save()
        
        saved_variant = ProductVariant.objects.get(id=variant.id)
        self.assertEqual(saved_variant.stock_quantity, 15)
        
        # Test stock decrease
        variant.stock_quantity -= 3
        variant.save()
        
        saved_variant = ProductVariant.objects.get(id=variant.id)
        self.assertEqual(saved_variant.stock_quantity, 12)
        
        # Test stock depletion
        variant.stock_quantity = 0
        variant.save()
        
        saved_variant = ProductVariant.objects.get(id=variant.id)
        self.assertEqual(saved_variant.stock_quantity, 0)
    
    def test_product_variant_price_management(self):
        """Test ProductVariant price management operations"""
        variant = ProductVariant.objects.create(
            color=self.color,
            size=self.size,
            stock_quantity=10,
            price=Decimal("99.99")
        )
        
        # Test price increase
        variant.price = Decimal("129.99")
        variant.save()
        
        saved_variant = ProductVariant.objects.get(id=variant.id)
        self.assertEqual(saved_variant.price, Decimal("129.99"))
        
        # Test price decrease
        variant.price = Decimal("79.99")
        variant.save()
        
        saved_variant = ProductVariant.objects.get(id=variant.id)
        self.assertEqual(saved_variant.price, Decimal("79.99"))
        
        # Test price with discount calculation
        original_price = Decimal("100.00")
        discount_percentage = 20
        discounted_price = original_price * (Decimal('1') - Decimal(discount_percentage) / Decimal('100'))
        
        variant.price = discounted_price
        variant.save()
        
        saved_variant = ProductVariant.objects.get(id=variant.id)
        self.assertEqual(saved_variant.price, Decimal("80.00"))
    
    def test_product_variant_availability_check(self):
        """Test ProductVariant availability checking logic"""
        # Create variant with stock
        variant = ProductVariant.objects.create(
            color=self.color,
            size=self.size,
            stock_quantity=10,
            price=Decimal("99.99")
        )
        
        # Test availability with stock
        is_available = variant.stock_quantity > 0
        self.assertTrue(is_available)
        
        # Test availability without stock
        variant.stock_quantity = 0
        variant.save()
        
        is_available = variant.stock_quantity > 0
        self.assertFalse(is_available)
        
        # Test availability with negative stock
        variant.stock_quantity = -5
        variant.save()
        
        is_available = variant.stock_quantity > 0
        self.assertFalse(is_available)
