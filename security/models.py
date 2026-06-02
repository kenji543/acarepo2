from django.db import models
import uuid


class HoneypotField(models.Model):
    """Honeypot trap to detect automated attacks."""
    TRAP_TYPES = (
        ('login_form', 'Login Form'),
        ('contact_form', 'Contact Form'),
        ('upload_form', 'Upload Form'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trap_type = models.CharField(max_length=50, choices=TRAP_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    form_data = models.JSONField(default=dict)
    triggered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Honeypot Field'
        verbose_name_plural = 'Honeypot Fields'
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['ip_address', 'triggered_at']),
        ]
    
    def __str__(self):
        return f"{self.trap_type} - {self.ip_address} - {self.triggered_at}"


class ThreatAlert(models.Model):
    """Track security threats and suspicious activity."""
    THREAT_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    THREAT_TYPES = (
        ('brute_force', 'Brute Force Attack'),
        ('idor', 'IDOR Attempt'),
        ('sql_injection', 'SQL Injection Attempt'),
        ('xss_attempt', 'XSS Attempt'),
        ('rate_limit_exceed', 'Rate Limit Exceeded'),
        ('honeypot_triggered', 'Honeypot Triggered'),
        ('suspicious_access', 'Suspicious Access Pattern'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    threat_type = models.CharField(max_length=50, choices=THREAT_TYPES)
    threat_level = models.CharField(max_length=20, choices=THREAT_LEVELS, default='medium')
    ip_address = models.GenericIPAddressField()
    description = models.TextField()
    
    # Detection details
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Response
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Threat Alert'
        verbose_name_plural = 'Threat Alerts'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['threat_type', 'is_resolved', 'detected_at']),
            models.Index(fields=['ip_address', 'threat_level']),
        ]
    
    def __str__(self):
        return f"{self.threat_type} - {self.threat_level} - {self.ip_address}"


class IPWhitelist(models.Model):
    """Whitelist trusted IP addresses."""
    ip_address = models.GenericIPAddressField(unique=True)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'IP Whitelist'
        verbose_name_plural = 'IP Whitelists'
    
    def __str__(self):
        return self.ip_address


class IPBlacklist(models.Model):
    """Blacklist suspicious IP addresses."""
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=255)
    severity = models.CharField(
        max_length=20,
        choices=[('temporary', 'Temporary'), ('permanent', 'Permanent')],
        default='temporary'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'IP Blacklist'
        verbose_name_plural = 'IP Blacklists'
    
    def __str__(self):
        return f"{self.ip_address} - {self.reason}"
