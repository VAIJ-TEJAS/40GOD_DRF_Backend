from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from product.models import Product, Color, Image, Size, Tag
from category.models import Category
from inventory.models import ProductVariant


class ProductPipelineTest(TransactionTestCase):
    """Test product functionality end-to-end"""
    
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
        self.tag = Tag.objects.create(text="Electronics")
    
    def test_product_creation_workflow(self):
        """Test complete product creation workflow"""
        # 1. Create product
        product_data = {
            'sku': 'WORKFLOW001',
            'name': 'Workflow Product',
            'description': 'Created via workflow',
            'price': '149.99',
            'category': self.category.id
        }
        
        # 2. Add colors to product
        color1 = Color.objects.create(
            product=self.product,
            display_name="Blue",
            color_name="Blue",
            hex_code="#0000FF"
        )
        color2 = Color.objects.create(
            product=self.product,
            display_name="Green",
            color_name="Green",
            hex_code="#00FF00"
        )
        
        # 3. Create variants
        variant1 = ProductVariant.objects.create(
            color=color1,
            size=self.size,
            stock_quantity=10,
            price=Decimal("149.99")
        )
        variant2 = ProductVariant.objects.create(
            color=color2,
            size=self.size,
            stock_quantity=5,
            price=Decimal("149.99")
        )
        
        # 4. Add tags
        self.product.tags.add(self.tag)
        
        # 5. Verify complete product setup
        colors = self.product.color_product.all()
        variants = ProductVariant.objects.filter(color__product=self.product)
        tags = self.product.tags.all()
        
        self.assertEqual(colors.count(), 3)  # Red + Blue + Green
        self.assertEqual(variants.count(), 2)
        self.assertEqual(tags.count(), 1)
        self.assertIn(self.tag, tags)
    
    def test_product_search_workflow(self):
        """Test product search and filtering workflow"""
        # Create additional products
        product2 = Product.objects.create(
            sku="SEARCH001",
            name="Search Product",
            description="For testing search",
            price=Decimal("79.99"),
            category=self.category
        )
        
        # Add tags for search
        search_tag = Tag.objects.create(text="Searchable")
        product2.tags.add(search_tag)
        
        # Test search by name
        products_by_name = Product.objects.filter(name__icontains="search")
        self.assertIn(product2, products_by_name)
        self.assertNotIn(self.product, products_by_name)
        
        # Test search by SKU
        products_by_sku = Product.objects.filter(sku__icontains="SEARCH")
        self.assertIn(product2, products_by_sku)
        self.assertNotIn(self.product, products_by_sku)
        
        # Test search by tag
        products_by_tag = Product.objects.filter(tags__text="Searchable")
        self.assertIn(product2, products_by_tag)
        self.assertNotIn(self.product, products_by_tag)
    
    def test_product_pricing_workflow(self):
        """Test product pricing and variant pricing workflow"""
        # Create variant with different price
        variant = ProductVariant.objects.create(
            color=self.color,
            size=self.size,
            stock_quantity=10,
            price=Decimal("129.99")  # Different from base product
        )
        
        # Test base product price
        self.assertEqual(self.product.price, Decimal("99.99"))
        
        # Test variant price
        self.assertEqual(variant.price, Decimal("129.99"))
        
        # Test price calculations
        total_value = variant.price * variant.stock_quantity
        self.assertEqual(total_value, Decimal("1299.90"))
    
    def test_product_image_workflow(self):
        """Test product image management workflow"""
        # Create additional colors for images
        color2 = Color.objects.create(
            product=self.product,
            display_name="Blue",
            color_name="Blue",
            hex_code="#0000FF"
        )
        
        # Add images to colors
        # Note: In real implementation, you'd upload actual image files
        # For testing, we'll verify the relationship structure
        
        # Test color-image relationship
        self.assertEqual(self.color.image_color.count(), 0)
        self.assertEqual(color2.image_color.count(), 0)
        
        # Verify color has product relationship
        self.assertEqual(self.color.product, self.product)
        self.assertEqual(color2.product, self.product)
    
    def test_product_category_workflow(self):
        """Test product categorization workflow"""
        # Create additional categories
        sub_category = Category.objects.create(
            name="Smartphones",
            parent=self.category
        )
        
        # Create product in subcategory
        sub_product = Product.objects.create(
            sku="SUB001",
            name="Smartphone",
            description="A smartphone product",
            price=Decimal("699.99"),
            category=sub_category
        )
        
        # Test category relationships
        self.assertEqual(sub_product.category, sub_category)
        self.assertEqual(sub_category.parent, self.category)
        
        # Test category filtering
        main_category_products = Product.objects.filter(category=self.category)
        sub_category_products = Product.objects.filter(category=sub_category)
        
        self.assertIn(self.product, main_category_products)
        self.assertNotIn(sub_product, main_category_products)
        self.assertIn(sub_product, sub_category_products)
    
    def test_product_variant_workflow(self):
        """Test product variant management workflow"""
        # Create multiple sizes
        sizes = [
            Size.objects.create(text="Small"),
            Size.objects.create(text="Medium"),
            Size.objects.create(text="Large")
        ]
        
        # Create variants for each size
        variants = []
        for size in sizes:
            variant = ProductVariant.objects.create(
                color=self.color,
                size=size,
                stock_quantity=10,
                price=Decimal("99.99")
            )
            variants.append(variant)
        
        # Test variant relationships
        for variant in variants:
            self.assertEqual(variant.color, self.color)
            self.assertIn(variant.size, sizes)
            self.assertEqual(variant.stock_quantity, 10)
        
        # Test filtering variants by color
        color_variants = ProductVariant.objects.filter(color=self.color)
        self.assertEqual(color_variants.count(), 3)
        
        # Test filtering variants by size
        large_variants = ProductVariant.objects.filter(size__text="Large")
        self.assertEqual(large_variants.count(), 1)
        self.assertEqual(large_variants.first().size.text, "Large")
    
    def test_product_inventory_workflow(self):
        """Test product inventory tracking workflow"""
        # Create variant with limited stock
        variant = ProductVariant.objects.create(
            color=self.color,
            size=self.size,
            stock_quantity=5,
            price=Decimal("99.99")
        )
        
        # Test initial stock
        self.assertEqual(variant.stock_quantity, 5)
        
        # Test stock availability check
        is_available = variant.stock_quantity > 0
        self.assertTrue(is_available)
        
        # Test stock depletion simulation
        variant.stock_quantity = 0
        variant.save()
        
        is_available = variant.stock_quantity > 0
        self.assertFalse(is_available)
        
        # Test restocking
        variant.stock_quantity = 10
        variant.save()
        
        is_available = variant.stock_quantity > 0
        self.assertTrue(is_available)
        self.assertEqual(variant.stock_quantity, 10)
