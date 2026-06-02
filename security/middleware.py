from django.utils.decorators import decorator_from_middleware
from django.utils.deprecation import MiddlewareNotUsed
from .models import ThreatAlert, IPBlacklist, HoneypotField
from django.utils import timezone
import logging

logger = logging.getLogger('django.security')


class SecurityMiddleware:
    """Middleware to detect and respond to security threats."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if IP is blacklisted
        ip = self.get_client_ip(request)
        
        if self.is_ip_blacklisted(ip):
            logger.warning(f"Blocked request from blacklisted IP: {ip}")
            return self.get_response(request)
        
        # Check for suspicious patterns
        self.check_suspicious_patterns(request, ip)
        
        response = self.get_response(request)
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def is_ip_blacklisted(ip):
        """Check if IP is blacklisted."""
        blacklist = IPBlacklist.objects.filter(ip_address=ip)
        for entry in blacklist:
            if entry.severity == 'permanent':
                return True
            if entry.expires_at and entry.expires_at > timezone.now():
                return True
        return False
    
    @staticmethod
    def check_suspicious_patterns(request, ip):
        """Check for common attack patterns."""
        suspicious_patterns = [
            'union select',
            'or 1=1',
            '../',
            '<script',
            'javascript:',
            'eval(',
        ]
        
        # Get request body and query string
        full_request = str(request.GET) + str(request.POST)
        
        for pattern in suspicious_patterns:
            if pattern.lower() in full_request.lower():
                ThreatAlert.objects.create(
                    threat_type='sql_injection',
                    threat_level='high',
                    ip_address=ip,
                    description=f'Potential SQL injection detected: {pattern}',
                    request_path=request.path,
                    request_method=request.method,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                logger.warning(f"Suspicious pattern detected from {ip}: {pattern}")


class HoneypotMiddleware:
    """Middleware to detect honeypot field triggers."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.method == 'POST' and request.POST.get('honeypot'):
            ip = self.get_client_ip(request)
            
            # Log honeypot trigger
            HoneypotField.objects.create(
                trap_type='contact_form',
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                form_data=dict(request.POST)
            )
            
            # Create threat alert
            ThreatAlert.objects.create(
                threat_type='honeypot_triggered',
                threat_level='medium',
                ip_address=ip,
                description='Honeypot field triggered - likely automated attack',
                request_path=request.path,
                request_method=request.method,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            logger.warning(f"Honeypot triggered from {ip}")
        
        return self.get_response(request)
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
