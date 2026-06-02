"""
Django settings validation tests
"""

import os
from django.test import TestCase
from django.conf import settings


class SettingsValidationTest(TestCase):
    """Test that critical settings are configured correctly."""
    
    def test_debug_disabled_in_production(self):
        """DEBUG should be False in production."""
        if os.environ.get('ENVIRONMENT') == 'production':
            self.assertFalse(settings.DEBUG)
    
    def test_secret_key_configured(self):
        """SECRET_KEY must be set."""
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertGreater(len(settings.SECRET_KEY), 20)
    
    def test_allowed_hosts_configured(self):
        """ALLOWED_HOSTS must be configured."""
        self.assertTrue(len(settings.ALLOWED_HOSTS) > 0)
    
    def test_database_configured(self):
        """Database must be configured."""
        self.assertIn('default', settings.DATABASES)
    
    def test_security_middleware_installed(self):
        """Security middleware must be installed."""
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'axes.middleware.AxesMiddleware',
        ]
        for middleware in required_middleware:
            self.assertIn(middleware, settings.MIDDLEWARE)
    
    def test_jwt_configured(self):
        """JWT settings must be configured."""
        self.assertIn('SIMPLE_JWT', settings.__dict__)
        self.assertGreater(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(), 0)
    
    def test_https_redirect_in_production(self):
        """SECURE_SSL_REDIRECT should be True in production."""
        if os.environ.get('ENVIRONMENT') == 'production':
            self.assertTrue(settings.SECURE_SSL_REDIRECT)
    
    def test_security_headers_configured(self):
        """Security headers must be configured."""
        self.assertTrue(settings.SECURE_BROWSER_XSS_FILTER)
        self.assertEqual(settings.X_FRAME_OPTIONS, 'DENY')
    
    def test_cors_configured(self):
        """CORS must be properly configured."""
        self.assertTrue(len(settings.CORS_ALLOWED_ORIGINS) > 0)
    
    def test_logging_configured(self):
        """Logging must be configured."""
        self.assertIn('LOGGING', settings.__dict__)
        self.assertIn('django', settings.LOGGING.get('loggers', {}))
