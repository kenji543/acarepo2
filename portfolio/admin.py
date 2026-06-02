from django.contrib import admin
from .models import (
    ResearcherProfile, ResearchPaper, CoAuthor, Dataset,
    AccessPermission, FileAccessLog
)


@admin.register(ResearcherProfile)
class ResearcherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'tier', 'created_at')
    list_filter = ('tier', 'created_at')
    search_fields = ('user__username', 'institution', 'orcid_id')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ResearchPaper)
class ResearchPaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'researcher', 'status', 'visibility', 'publication_date')
    list_filter = ('status', 'visibility', 'created_at')
    search_fields = ('title', 'doi', 'researcher__user__username')
    readonly_fields = ('id', 'created_at', 'updated_at', 'view_count', 'download_count')
    fieldsets = (
        ('Paper Information', {
            'fields': ('researcher', 'title', 'abstract', 'keywords', 'publication_date', 'doi')
        }),
        ('Files', {
            'fields': ('pdf_file', 'supplementary_data', 'raw_data_file')
        }),
        ('Access Control', {
            'fields': ('status', 'visibility')
        }),
        ('Analytics', {
            'fields': ('view_count', 'download_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class CoAuthorInline(admin.TabularInline):
    model = CoAuthor
    extra = 1
    fields = ('author_name', 'author_email', 'author_institution', 'order')


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('title', 'researcher', 'status', 'visibility', 'file_format')
    list_filter = ('status', 'visibility', 'file_format', 'created_at')
    search_fields = ('title', 'researcher__user__username')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(AccessPermission)
class AccessPermissionAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'permission_type', 'granted_by', 'is_active', 'granted_at')
    list_filter = ('permission_type', 'is_active', 'granted_at')
    search_fields = ('reviewer__username', 'paper__title', 'dataset__title')
    readonly_fields = ('id', 'granted_at')


@admin.register(FileAccessLog)
class FileAccessLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'access_type', 'ip_address', 'accessed_at')
    list_filter = ('access_type', 'accessed_at')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('id', 'accessed_at')
    date_hierarchy = 'accessed_at'
