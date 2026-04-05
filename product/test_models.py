from django.test import TestCase
from django.contrib.auth.models import User
from product.models import Product, Category, Review

class ProductModelTest(TestCase):
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
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=99.99,
            category=self.category,
            stock_quantity=10,
            seller=self.user
        )
    
    def test_product_creation(self):
        """Test product creation with all fields"""
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.price, 99.99)
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.seller, self.user)
        self.assertEqual(self.product.stock_quantity, 10)
    
    def test_product_str_method(self):
        """Test string representation of product"""
        expected_str = f"{self.product.name} - ${self.product.price}"
        self.assertEqual(str(self.product), expected_str)
    
    def test_category_creation(self):
        """Test category creation"""
        self.assertEqual(self.category.name, 'Electronics')
        self.assertEqual(self.category.description, 'Electronic devices')
        self.assertEqual(str(self.category), 'Electronics')
    
    def test_review_creation(self):
        """Test review creation for product"""
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Excellent product!'
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.user)
    
    def test_product_stock_update(self):
        """Test product stock quantity update"""
        self.product.stock_quantity = 5
        self.product.save()
        self.assertEqual(self.product.stock_quantity, 5)
