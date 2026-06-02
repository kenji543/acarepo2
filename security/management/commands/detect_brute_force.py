from django.core.management.base import BaseCommand
from django.utils import timezone
from security.models import IPBlacklist
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Detect brute force attacks and automatically blacklist suspicious IPs'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--threshold',
            type=int,
            default=10,
            help='Number of failed attempts to trigger blacklisting'
        )
        parser.add_argument(
            '--duration',
            type=int,
            default=3600,
            help='Blacklist duration in seconds'
        )
    
    def handle(self, *args, **options):
        from auth_service.models import AuditLog
        from security.models import ThreatAlert
        
        threshold = options['threshold']
        duration = options['duration']
        
        # Analyze failed login attempts in last hour
        one_hour_ago = timezone.now() - timedelta(hours=1)
        failed_attempts = AuditLog.objects.filter(
            event_type='failed_login',
            timestamp__gte=one_hour_ago
        ).values('ip_address').annotate(count=models.Count('id'))
        
        for attempt in failed_attempts:
            if attempt['count'] >= threshold:
                ip = attempt['ip_address']
                
                # Check if already blacklisted
                if not IPBlacklist.objects.filter(ip_address=ip, severity='permanent').exists():
                    # Create temporary blacklist entry
                    IPBlacklist.objects.create(
                        ip_address=ip,
                        reason=f'Brute force attack detected ({attempt["count"]} failed attempts)',
                        severity='temporary',
                        expires_at=timezone.now() + timedelta(seconds=duration)
                    )
                    
                    # Create threat alert
                    ThreatAlert.objects.create(
                        threat_type='brute_force',
                        threat_level='high',
                        ip_address=ip,
                        description=f'{attempt["count"]} failed login attempts detected'
                    )
                    
                    self.stdout.write(
                        self.style.WARNING(f'Blacklisted IP: {ip} ({attempt["count"]} attempts)')
                    )
                    logger.warning(f'Brute force blacklist created for {ip}')
