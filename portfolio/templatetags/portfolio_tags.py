from django import template
from django.template.defaultfilters import filesizeformat
from portfolio.models import FileAccessLog
from datetime import timedelta
from django.utils import timezone

register = template.Library()


@register.filter
def format_file_size(bytes_size):
    """Format bytes to human-readable file size."""
    if not bytes_size:
        return "0 B"
    return filesizeformat(bytes_size)


@register.filter
def access_count(obj, access_type=None):
    """Get access count for paper or dataset."""
    if access_type:
        return FileAccessLog.objects.filter(
            paper=obj if hasattr(obj, 'pdf_file') else None,
            access_type=access_type
        ).count()
    return FileAccessLog.objects.filter(
        paper=obj if hasattr(obj, 'pdf_file') else None
    ).count()


@register.simple_tag
def get_recent_access(obj, days=7):
    """Get access logs from last N days."""
    cutoff = timezone.now() - timedelta(days=days)
    return FileAccessLog.objects.filter(
        paper=obj if hasattr(obj, 'pdf_file') else None,
        accessed_at__gte=cutoff
    ).order_by('-accessed_at')
