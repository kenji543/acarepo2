"""
API Integration Tests
"""

from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from portfolio.models import ResearcherProfile, ResearchPaper
from datetime import datetime


class APIAuthenticationTest(APITestCase):
    """Test authentication endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
    
    def test_user_registration(self):
        """Test user registration."""
        response = self.client.post('/auth/api/register/', self.user_data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_user_login(self):
        """Test user login."""
        # Create user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!'
        )
        
        # Login
        response = self.client.post('/auth/api/login/', {
            'username': 'testuser',
            'password': 'TestPassword123!'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post('/auth/api/login/', {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 401)


class APIResearcherProfileTest(APITestCase):
    """Test researcher profile endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='researcher',
            email='researcher@example.com',
            password='TestPassword123!'
        )
        
        # Create researcher profile
        self.profile = ResearcherProfile.objects.create(
            user=self.user,
            institution='MIT',
            tier='basic'
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_get_my_profile(self):
        """Test retrieving current user profile."""
        response = self.client.get('/api/researchers/my-profile/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'researcher')
    
    def test_list_researchers(self):
        """Test listing researchers."""
        response = self.client.get('/api/researchers/')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['results']), 0)


class APIPermissionTest(APITestCase):
    """Test permission and access control."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.owner = User.objects.create_user(username='owner', password='pass')
        self.other_user = User.objects.create_user(username='other', password='pass')
        
        # Create profiles
        ResearcherProfile.objects.create(user=self.owner, tier='basic')
        ResearcherProfile.objects.create(user=self.other_user, tier='basic')
    
    def test_owner_can_access_own_profile(self):
        """Owner should access their own profile."""
        refresh = RefreshToken.for_user(self.owner)
        token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.get('/api/researchers/my-profile/')
        self.assertEqual(response.status_code, 200)
    
    def test_unauthenticated_cannot_update_profile(self):
        """Unauthenticated users cannot update profiles."""
        response = self.client.put('/api/researchers/1/', {})
        self.assertEqual(response.status_code, 401)
