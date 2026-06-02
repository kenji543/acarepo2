from django.core.management.base import BaseCommand
from django.utils import timezone
from security.models import IPBlacklist, ThreatAlert
from datetime import timedelta


class Command(BaseCommand):
    help = 'Security maintenance: clean up expired blacklist entries and old threat logs'
    
    def handle(self, *args, **options):
        # Remove expired temporary blacklist entries
        expired_count = IPBlacklist.objects.filter(
            severity='temporary',
            expires_at__lt=timezone.now()
        ).delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(f'Removed {expired_count} expired blacklist entries')
        )
        
        # Archive old threat alerts (older than 90 days)
        old_date = timezone.now() - timedelta(days=90)
        old_alerts = ThreatAlert.objects.filter(
            detected_at__lt=old_date,
            is_resolved=True
        ).count()
        
        self.stdout.write(
            self.style.SUCCESS(f'Found {old_alerts} old threat alerts for archival')
        )
