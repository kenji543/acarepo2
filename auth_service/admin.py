from django.contrib import admin
from .models import TokenBlacklist, AuditLog


@admin.register(TokenBlacklist)
class TokenBlacklistAdmin(admin.ModelAdmin):
    list_display = ('user', 'blacklisted_at', 'expires_at')
    list_filter = ('blacklisted_at', 'expires_at')
    search_fields = ('user__username',)
    readonly_fields = ('id', 'blacklisted_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_type', 'ip_address', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('user__username', 'ip_address', 'description')
    readonly_fields = ('id', 'timestamp')
    date_hierarchy = 'timestamp'
