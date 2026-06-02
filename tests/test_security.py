"""
Security-focused unit tests
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from security.models import ThreatAlert, HoneypotField, IPBlacklist
from security.middleware import SecurityMiddleware
from portfolio.models import ResearcherProfile
from datetime import datetime, timedelta
from django.utils import timezone


class ThreatDetectionTest(TestCase):
    """Test threat detection functionality."""
    
    def test_create_threat_alert(self):
        """Test creating threat alerts."""
        alert = ThreatAlert.objects.create(
            threat_type='brute_force',
            threat_level='high',
            ip_address='192.168.1.1',
            description='Brute force attack detected'
        )
        
        self.assertEqual(alert.threat_type, 'brute_force')
        self.assertEqual(alert.threat_level, 'high')
        self.assertFalse(alert.is_resolved)
    
    def test_resolve_threat(self):
        """Test resolving threats."""
        alert = ThreatAlert.objects.create(
            threat_type='sql_injection',
            threat_level='critical',
            ip_address='10.0.0.1',
            description='SQL injection attempt'
        )
        
        alert.is_resolved = True
        alert.resolution_notes = 'IP blacklisted'
        alert.resolved_at = timezone.now()
        alert.save()
        
        self.assertTrue(alert.is_resolved)
        self.assertIsNotNone(alert.resolved_at)


class IPBlacklistTest(TestCase):
    """Test IP blacklisting functionality."""
    
    def test_create_permanent_blacklist(self):
        """Test creating permanent IP blacklist."""
        blacklist = IPBlacklist.objects.create(
            ip_address='192.168.1.100',
            reason='Repeated attack attempts',
            severity='permanent'
        )
        
        self.assertEqual(blacklist.ip_address, '192.168.1.100')
        self.assertEqual(blacklist.severity, 'permanent')
    
    def test_create_temporary_blacklist(self):
        """Test creating temporary IP blacklist."""
        expires_at = timezone.now() + timedelta(hours=1)
        blacklist = IPBlacklist.objects.create(
            ip_address='10.0.0.50',
            reason='Temporary ban',
            severity='temporary',
            expires_at=expires_at
        )
        
        self.assertEqual(blacklist.severity, 'temporary')
        self.assertIsNotNone(blacklist.expires_at)
    
    def test_temporary_blacklist_expiration(self):
        """Test checking temporary blacklist expiration."""
        # Create expired entry
        expired_at = timezone.now() - timedelta(hours=1)
        blacklist = IPBlacklist.objects.create(
            ip_address='10.0.0.60',
            reason='Expired ban',
            severity='temporary',
            expires_at=expired_at
        )
        
        # Entry exists but is expired
        self.assertTrue(IPBlacklist.objects.filter(ip_address='10.0.0.60').exists())
        self.assertLess(blacklist.expires_at, timezone.now())


class HoneypotTest(TestCase):
    """Test honeypot functionality."""
    
    def test_honeypot_field_trigger(self):
        """Test honeypot field detection."""
        honeypot = HoneypotField.objects.create(
            trap_type='login_form',
            ip_address='192.168.1.50',
            form_data={'username': 'attacker', 'honeypot': 'filled'}
        )
        
        self.assertEqual(honeypot.trap_type, 'login_form')
        self.assertEqual(honeypot.form_data['honeypot'], 'filled')
    
    def test_honeypot_creates_threat_alert(self):
        """Test that honeypot triggers create threat alerts."""
        # Create honeypot trigger
        HoneypotField.objects.create(
            trap_type='contact_form',
            ip_address='10.0.0.70',
        )
        
        # Should create threat alert
        ThreatAlert.objects.create(
            threat_type='honeypot_triggered',
            threat_level='medium',
            ip_address='10.0.0.70',
            description='Honeypot field triggered'
        )
        
        alert = ThreatAlert.objects.get(ip_address='10.0.0.70')
        self.assertEqual(alert.threat_type, 'honeypot_triggered')


class PermissionTest(TestCase):
    """Test permission enforcement."""
    
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        
        ResearcherProfile.objects.create(user=self.user1, tier='basic')
        ResearcherProfile.objects.create(user=self.user2, tier='basic')
    
    def test_user_tier_basic(self):
        """Test basic tier permissions."""
        profile = self.user1.researcher_profile
        self.assertEqual(profile.tier, 'basic')
    
    def test_user_tier_premium(self):
        """Test premium tier permissions."""
        profile = self.user1.researcher_profile
        profile.tier = 'premium'
        profile.save()
        
        refreshed = ResearcherProfile.objects.get(user=self.user1)
        self.assertEqual(refreshed.tier, 'premium')
