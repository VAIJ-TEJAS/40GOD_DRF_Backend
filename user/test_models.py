from django.test import TestCase
from django.contrib.auth.models import User
from user.models import UserProfile

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """Test user profile is created automatically"""
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertFalse(profile.is_premium_member)
        self.assertEqual(profile.wallet_balance, 0)
    
    def test_user_profile_str_method(self):
        """Test string representation of user profile"""
        profile = UserProfile.objects.get(user=self.user)
        expected_str = f"{self.user.username}'s Profile"
        self.assertEqual(str(profile), expected_str)
    
    def test_premium_member_upgrade(self):
        """Test upgrading user to premium member"""
        profile = UserProfile.objects.get(user=self.user)
        profile.is_premium_member = True
        profile.save()
        self.assertTrue(profile.is_premium_member)
    
    def test_wallet_balance_update(self):
        """Test wallet balance updates"""
        profile = UserProfile.objects.get(user=self.user)
        profile.wallet_balance = 100.50
        profile.save()
        self.assertEqual(profile.wallet_balance, 100.50)
