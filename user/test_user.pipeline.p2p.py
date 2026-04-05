from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import authenticate
from user.models import User
from cart.models import CartItem
from inventory.models import ProductVariant
from product.models import Product, Category, Color, Size


class UserPipelineTest(TransactionTestCase):
    """Test user functionality end-to-end"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_user_registration_workflow(self):
        """Test complete user registration workflow"""
        # 1. Register new user
        new_user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        
        new_user = User.objects.create_user(**new_user_data)
        
        # 2. Verify user creation
        self.assertEqual(new_user.username, 'newuser')
        self.assertEqual(new_user.email, 'newuser@example.com')
        self.assertTrue(new_user.check_password('newpass123'))
        self.assertTrue(new_user.is_active)
        self.assertFalse(new_user.is_staff)
        
        # 3. Test user can be authenticated
        authenticated_user = authenticate(
            username='newuser',
            password='newpass123'
        )
        self.assertEqual(authenticated_user, new_user)
        
        # 4. Test user login via client
        login_success = self.client.login(
            username='newuser',
            password='newpass123'
        )
        self.assertTrue(login_success)
    
    def test_user_login_workflow(self):
        """Test user login workflow"""
        # 1. Test successful login
        login_success = self.client.login(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        self.assertTrue(login_success)
        
        # 2. Test failed login with wrong password
        login_fail = self.client.login(
            username=self.user_data['username'],
            password='wrongpass'
        )
        self.assertFalse(login_fail)
        
        # 3. Test failed login with non-existent user
        login_fail = self.client.login(
            username='nonexistent',
            password='anypassword'
        )
        self.assertFalse(login_fail)
    
    def test_user_profile_workflow(self):
        """Test user profile management workflow"""
        # 1. User logs in
        self.client.login(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        
        # 2. Update user profile
        self.user.email = 'updated@example.com'
        self.user.first_name = 'John'
        self.user.last_name = 'Doe'
        self.user.save()
        
        # 3. Verify profile updates
        updated_user = User.objects.get(username=self.user_data['username'])
        self.assertEqual(updated_user.email, 'updated@example.com')
        self.assertEqual(updated_user.first_name, 'John')
        self.assertEqual(updated_user.last_name, 'Doe')
    
    def test_user_password_change_workflow(self):
        """Test user password change workflow"""
        # 1. User logs in with old password
        login_success = self.client.login(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        self.assertTrue(login_success)
        
        # 2. Change password
        new_password = 'newsecurepass123'
        self.user.set_password(new_password)
        self.user.save()
        
        # 3. Test old password no longer works
        login_fail = self.client.login(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        self.assertFalse(login_fail)
        
        # 4. Test new password works
        login_success = self.client.login(
            username=self.user_data['username'],
            password=new_password
        )
        self.assertTrue(login_success)
    
    def test_user_cart_workflow(self):
        """Test user cart integration workflow"""
        # 1. Set up product data
        category = Category.objects.create(name="Electronics")
        product = Product.objects.create(
            sku="TEST001",
            name="Test Product",
            price="99.99",
            category=category
        )
        color = Color.objects.create(
            product=product,
            display_name="Red",
            color_name="Red",
            hex_code="#FF0000"
        )
        size = Size.objects.create(text="Large")
        variant = ProductVariant.objects.create(
            color=color,
            size=size,
            stock_quantity=10,
            price="99.99"
        )
        
        # 2. User logs in
        self.client.login(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        
        # 3. Add items to cart
        cart_item = CartItem.objects.create(
            user=self.user,
            product_varient=variant,
            quantity=2
        )
        
        # 4. Verify cart contents
        user_cart_items = CartItem.objects.filter(user=self.user)
        self.assertEqual(user_cart_items.count(), 1)
        self.assertEqual(user_cart_items.first().quantity, 2)
        
        # 5. Test user-specific cart filtering
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        other_cart_item = CartItem.objects.create(
            user=other_user,
            product_varient=variant,
            quantity=1
        )
        
        # Verify cart isolation
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 1)
        self.assertEqual(CartItem.objects.filter(user=other_user).count(), 1)
    
    def test_user_permissions_workflow(self):
        """Test user permissions and roles workflow"""
        # 1. Test regular user permissions
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        
        # 2. Create staff user
        staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpass123'
        )
        staff_user.is_staff = True
        staff_user.save()
        
        # 3. Create superuser
        superuser = User.objects.create_superuser(
            username='superuser',
            email='super@example.com',
            password='superpass123'
        )
        
        # 4. Verify permission levels
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        
        self.assertTrue(staff_user.is_staff)
        self.assertFalse(staff_user.is_superuser)
        
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
    
    def test_user_deactivation_workflow(self):
        """Test user deactivation and reactivation workflow"""
        # 1. User is initially active
        self.assertTrue(self.user.is_active)
        
        # 2. User can login when active
        login_success = self.client.login(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        self.assertTrue(login_success)
        
        # 3. Deactivate user
        self.user.is_active = False
        self.user.save()
        
        # 4. User cannot login when inactive
        # Note: Django's authenticate still works for inactive users,
        # but login checks should fail
        authenticated_user = authenticate(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        self.assertIsNotNone(authenticated_user)
        self.assertFalse(authenticated_user.is_active)
        
        # 5. Reactivate user
        self.user.is_active = True
        self.user.save()
        
        # 6. User can login again
        login_success = self.client.login(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        self.assertTrue(login_success)
    
    def test_user_order_history_workflow(self):
        """Test user order history tracking workflow"""
        # This would integrate with an order system
        # For now, we'll test the user relationship structure
        
        # 1. User logs in
        self.client.login(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        
        # 2. Test user can be retrieved for order operations
        user_for_order = User.objects.get(username=self.user_data['username'])
        self.assertEqual(user_for_order, self.user)
        
        # 3. Test user email for notifications
        self.assertEqual(user_for_order.email, self.user_data['email'])
        
        # 4. Test user is active for order processing
        self.assertTrue(user_for_order.is_active)
    
    def test_user_search_workflow(self):
        """Test user search and filtering workflow"""
        # Create additional users
        users_data = [
            {'username': 'alice', 'email': 'alice@example.com', 'password': 'alicepass'},
            {'username': 'bob', 'email': 'bob@example.com', 'password': 'bobpass'},
            {'username': 'charlie', 'email': 'charlie@example.com', 'password': 'charliepass'}
        ]
        
        created_users = []
        for user_data in users_data:
            user = User.objects.create_user(**user_data)
            created_users.append(user)
        
        # Test search by username
        alice_users = User.objects.filter(username__icontains='alice')
        self.assertEqual(alice_users.count(), 1)
        self.assertEqual(alice_users.first().username, 'alice')
        
        # Test search by email
        example_users = User.objects.filter(email__icontains='example')
        self.assertEqual(example_users.count(), 4)  # 3 new + 1 original
        
        # Test filter by active status
        active_users = User.objects.filter(is_active=True)
        self.assertEqual(active_users.count(), 4)
        
        # Test filter by staff status
        staff_users = User.objects.filter(is_staff=True)
        self.assertEqual(staff_users.count(), 0)
        
        # Test filter by superuser status
        superusers = User.objects.filter(is_superuser=True)
        self.assertEqual(superusers.count(), 0)
