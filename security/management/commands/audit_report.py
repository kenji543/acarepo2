from django.core.management.base import BaseCommand
from django.db import models


class Command(BaseCommand):
    help = 'Generate security audit report'
    
    def handle(self, *args, **options):
        from auth_service.models import AuditLog
        from security.models import ThreatAlert
        from django.utils import timezone
        from datetime import timedelta
        
        # Get statistics from last 24 hours
        cutoff = timezone.now() - timedelta(hours=24)
        
        total_logins = AuditLog.objects.filter(
            event_type='login',
            timestamp__gte=cutoff
        ).count()
        
        failed_logins = AuditLog.objects.filter(
            event_type='failed_login',
            timestamp__gte=cutoff
        ).count()
        
        threats = ThreatAlert.objects.filter(
            detected_at__gte=cutoff,
            threat_level__in=['high', 'critical']
        ).count()
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.WARNING("SECURITY AUDIT REPORT - Last 24 Hours"))
        self.stdout.write("="*50)
        self.stdout.write(f"Total Logins: {total_logins}")
        self.stdout.write(self.style.WARNING(f"Failed Logins: {failed_logins}"))
        self.stdout.write(self.style.ERROR(f"High/Critical Threats: {threats}"))
        self.stdout.write("="*50 + "\n")
