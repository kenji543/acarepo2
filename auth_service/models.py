from django.db import models
from django.contrib.auth.models import User
import uuid


class TokenBlacklist(models.Model):
    """Track blacklisted JWT tokens for logout functionality."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blacklisted_tokens')
    token = models.TextField()
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        verbose_name = 'Token Blacklist'
        verbose_name_plural = 'Token Blacklists'
        indexes = [
            models.Index(fields=['user', 'blacklisted_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.blacklisted_at}"


class AuditLog(models.Model):
    """Comprehensive audit logging for security events."""
    EVENT_TYPES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('registration', 'Registration'),
        ('token_refresh', 'Token Refresh'),
        ('failed_login', 'Failed Login'),
        ('permission_change', 'Permission Change'),
        ('file_access', 'File Access'),
        ('data_export', 'Data Export'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.event_type} - {self.timestamp}"
