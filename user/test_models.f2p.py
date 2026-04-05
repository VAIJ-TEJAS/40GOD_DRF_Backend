from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from user.models import User


class UserModelTest(TestCase):
    """Test User model functionality"""
    
    def test_user_creation(self):
        """Test User can be created successfully"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(user.id)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_user_str_method(self):
        """Test User string representation"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        self.assertEqual(str(user), "testuser")
    
    def test_user_email_unique(self):
        """Test User email must be unique"""
        User.objects.create_user(
            username="testuser1",
            email="test@example.com",
            password="testpass123"
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="testuser2",
                email="test@example.com",
                password="testpass123"
            )
    
    def test_user_username_unique(self):
        """Test User username must be unique"""
        User.objects.create_user(
            username="testuser",
            email="test1@example.com",
            password="testpass123"
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="testuser",
                email="test2@example.com",
                password="testpass123"
            )
    
    def test_user_password_hashing(self):
        """Test User password is properly hashed"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        # Password should be hashed, not stored in plain text
        self.assertNotEqual(user.password, "testpass123")
        self.assertTrue(user.password.startswith("pbkdf2_sha256$") or 
                       user.password.startswith("bcrypt$") or
                       user.password.startswith("argon2$"))
    
    def test_user_check_password(self):
        """Test User password checking"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        # Correct password
        self.assertTrue(user.check_password("testpass123"))
        
        # Incorrect password
        self.assertFalse(user.check_password("wrongpass"))
    
    def test_user_create_superuser(self):
        """Test creating superuser"""
        superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )
        
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
    
    def test_user_email_normalization(self):
        """Test User email normalization"""
        user = User.objects.create_user(
            username="testuser",
            email="Test@Example.COM",
            password="testpass123"
        )
        
        self.assertEqual(user.email, "Test@example.com")
    
    def test_user_required_fields(self):
        """Test User required fields"""
        # Test without username
        with self.assertRaises(TypeError):
            User.objects.create_user(
                email="test@example.com",
                password="testpass123"
            )
        
        # Test without email
        with self.assertRaises(TypeError):
            User.objects.create_user(
                username="testuser",
                password="testpass123"
            )
        
        # Test without password
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
        
        # Password should be unusable
        self.assertFalse(user.has_usable_password())
    
    def test_user_update_email(self):
        """Test updating user email"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        # Update email
        user.email = "newemail@example.com"
        user.save()
        
        updated_user = User.objects.get(username="testuser")
        self.assertEqual(updated_user.email, "newemail@example.com")
    
    def test_user_update_password(self):
        """Test updating user password"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        # Update password
        user.set_password("newpass123")
        user.save()
        
        updated_user = User.objects.get(username="testuser")
        self.assertTrue(updated_user.check_password("newpass123"))
        self.assertFalse(updated_user.check_password("testpass123"))
    
    def test_user_is_active_default(self):
        """Test User is active by default"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        self.assertTrue(user.is_active)
    
    def test_user_deactivate(self):
        """Test deactivating user"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        # Deactivate user
        user.is_active = False
        user.save()
        
        updated_user = User.objects.get(username="testuser")
        self.assertFalse(updated_user.is_active)
    
    def test_user_queryset_manager(self):
        """Test User custom queryset manager if exists"""
        # Create multiple users
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123"
        )
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123"
        )
        
        # Test basic queryset
        all_users = User.objects.all()
        self.assertEqual(all_users.count(), 2)
        
        # Test filtering
        active_users = User.objects.filter(is_active=True)
        self.assertEqual(active_users.count(), 2)
        
        # Test get
        retrieved_user = User.objects.get(username="user1")
        self.assertEqual(retrieved_user, user1)
