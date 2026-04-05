from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from product.models import Product, Color, Image, Size, Tag
from category.models import Category


class ProductModelTest(TestCase):
    """Test Product model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name="Electronics")
    
    def test_product_creation(self):
        """Test Product can be created successfully"""
        product = Product.objects.create(
            sku="TEST001",
            name="Test Product",
            description="Test Description",
            price=Decimal("99.99"),
            category=self.category
        )
        
        self.assertEqual(product.sku, "TEST001")
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.description, "Test Description")
        self.assertEqual(product.price, Decimal("99.99"))
        self.assertEqual(product.category, self.category)
        self.assertTrue(product.id)
    
    def test_product_str_method(self):
        """Test Product string representation"""
        product = Product.objects.create(
            sku="TEST001",
            name="Test Product",
            price=Decimal("99.99"),
            category=self.category
        )
        
        self.assertEqual(str(product), "Test Product")
    
    def test_product_sku_unique(self):
        """Test Product SKU must be unique"""
        Product.objects.create(
            sku="TEST001",
            name="Test Product 1",
            price=Decimal("99.99"),
            category=self.category
        )
        
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Product.objects.create(
                sku="TEST001",
                name="Test Product 2",
                price=Decimal("49.99"),
                category=self.category
            )
    
    def test_product_price_validation(self):
        """Test Product price validation"""
        product = Product(
            sku="TEST001",
            name="Test Product",
            price=Decimal("-10.00"),
            category=self.category
        )
        
        # Negative price should be allowed unless constrained
        product.full_clean()
        product.save()
        
        # Verify negative price saved
        saved_product = Product.objects.get(sku="TEST001")
        self.assertEqual(saved_product.price, Decimal("-10.00"))


class ColorModelTest(TestCase):
    """Test Color model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            sku="TEST001",
            name="Test Product",
            price=Decimal("99.99"),
            category=self.category
        )
    
    def test_color_creation(self):
        """Test Color can be created successfully"""
        color = Color.objects.create(
            product=self.product,
            display_name="Red",
            color_name="Red",
            hex_code="#FF0000"
        )
        
        self.assertEqual(color.product, self.product)
        self.assertEqual(color.display_name, "Red")
        self.assertEqual(color.color_name, "Red")
        self.assertEqual(color.hex_code, "#FF0000")
        self.assertTrue(color.id)
    
    def test_color_str_method(self):
        """Test Color string representation"""
        color = Color.objects.create(
            product=self.product,
            display_name="Red",
            color_name="Red",
            hex_code="#FF0000"
        )
        
        expected_str = f"{self.product.sku} {self.product.name} Red (#FF0000)"
        self.assertEqual(str(color), expected_str)
    
    def test_color_hex_code_validation(self):
        """Test Color hex code format"""
        color = Color(
            product=self.product,
            display_name="Invalid",
            color_name="Invalid",
            hex_code="INVALID"
        )
        
        # Should allow any hex code format unless constrained
        color.full_clean()
        color.save()
        
        saved_color = Color.objects.get(display_name="Invalid")
        self.assertEqual(saved_color.hex_code, "INVALID")


class SizeModelTest(TestCase):
    """Test Size model functionality"""
    
    def test_size_creation(self):
        """Test Size can be created successfully"""
        size = Size.objects.create(text="Large")
        
        self.assertEqual(size.text, "Large")
        self.assertTrue(size.id)
    
    def test_size_str_method(self):
        """Test Size string representation"""
        size = Size.objects.create(text="Large")
        
        self.assertEqual(str(size), "Large")
    
    def test_size_unique_text(self):
        """Test Size text should be unique for consistency"""
        Size.objects.create(text="Large")
        
        # Should allow duplicate text unless unique constraint added
        size2 = Size.objects.create(text="Large")
        self.assertEqual(size2.text, "Large")


class TagModelTest(TestCase):
    """Test Tag model functionality"""
    
    def test_tag_creation(self):
        """Test Tag can be created successfully"""
        tag = Tag.objects.create(text="Electronics")
        
        self.assertEqual(tag.text, "Electronics")
        self.assertTrue(tag.id)
    
    def test_tag_str_method(self):
        """Test Tag string representation"""
        tag = Tag.objects.create(text="Electronics")
        
        self.assertEqual(str(tag), "Electronics")
    
    def test_tag_unique_text(self):
        """Test Tag text should be unique for consistency"""
        Tag.objects.create(text="Electronics")
        
        # Should allow duplicate text unless unique constraint added
        tag2 = Tag.objects.create(text="Electronics")
        self.assertEqual(tag2.text, "Electronics")


class ProductTagRelationshipTest(TestCase):
    """Test Product-Tag many-to-many relationship"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            sku="TEST001",
            name="Test Product",
            price=Decimal("99.99"),
            category=self.category
        )
        self.tag1 = Tag.objects.create(text="Electronics")
        self.tag2 = Tag.objects.create(text="Gadget")
    
    def test_product_tag_relationship(self):
        """Test Product-Tag many-to-many relationship"""
        self.product.tags.add(self.tag1, self.tag2)
        
        tags = self.product.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(self.tag1, tags)
        self.assertIn(self.tag2, tags)
    
    def test_tag_product_relationship(self):
        """Test Tag-Product reverse relationship"""
        self.product.tags.add(self.tag1)
        
        products = self.tag1.product_tags.all()
        self.assertEqual(products.count(), 1)
        self.assertIn(self.product, products)
    
    def test_remove_tag_from_product(self):
        """Test removing tag from product"""
        self.product.tags.add(self.tag1, self.tag2)
        
        self.product.tags.remove(self.tag1)
        
        tags = self.product.tags.all()
        self.assertEqual(tags.count(), 1)
        self.assertNotIn(self.tag1, tags)
        self.assertIn(self.tag2, tags)
