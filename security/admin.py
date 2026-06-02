from django.contrib import admin
from .models import HoneypotField, ThreatAlert, IPWhitelist, IPBlacklist


@admin.register(HoneypotField)
class HoneypotFieldAdmin(admin.ModelAdmin):
    list_display = ('trap_type', 'ip_address', 'triggered_at')
    list_filter = ('trap_type', 'triggered_at')
    search_fields = ('ip_address',)
    readonly_fields = ('id', 'triggered_at', 'form_data')


@admin.register(ThreatAlert)
class ThreatAlertAdmin(admin.ModelAdmin):
    list_display = ('threat_type', 'threat_level', 'ip_address', 'detected_at', 'is_resolved')
    list_filter = ('threat_type', 'threat_level', 'is_resolved', 'detected_at')
    search_fields = ('ip_address', 'description')
    readonly_fields = ('id', 'detected_at')
    fieldsets = (
        ('Threat Information', {
            'fields': ('threat_type', 'threat_level', 'ip_address', 'description')
        }),
        ('Request Details', {
            'fields': ('request_path', 'request_method', 'user_agent'),
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolution_notes', 'resolved_at'),
        }),
        ('Metadata', {
            'fields': ('id', 'detected_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(IPWhitelist)
class IPWhitelistAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'description', 'created_at')
    search_fields = ('ip_address',)
    readonly_fields = ('created_at',)


@admin.register(IPBlacklist)
class IPBlacklistAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'reason', 'severity', 'expires_at')
    list_filter = ('severity', 'created_at')
    search_fields = ('ip_address', 'reason')
    readonly_fields = ('created_at',)
