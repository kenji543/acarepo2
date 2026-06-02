from rest_framework import serializers
from django.contrib.auth.models import User
from portfolio.models import (
    ResearcherProfile, ResearchPaper, CoAuthor, Dataset,
    AccessPermission, FileAccessLog
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ResearcherProfileSerializer(serializers.ModelSerializer):
    """Serializer for ResearcherProfile with nested user."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ResearcherProfile
        fields = [
            'id', 'user', 'bio', 'institution', 'department', 'position',
            'orcid_id', 'google_scholar', 'research_interests', 'tier',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CoAuthorSerializer(serializers.ModelSerializer):
    """Serializer for CoAuthor model."""
    class Meta:
        model = CoAuthor
        fields = ['id', 'author_name', 'author_email', 'author_institution', 'order']


class ResearchPaperSerializer(serializers.ModelSerializer):
    """Serializer for ResearchPaper with conditional field masking based on JWT tier."""
    researcher = ResearcherProfileSerializer(read_only=True)
    co_authors = CoAuthorSerializer(many=True, read_only=True)
    
    class Meta:
        model = ResearchPaper
        fields = [
            'id', 'researcher', 'title', 'abstract', 'keywords',
            'publication_date', 'doi', 'status', 'visibility',
            'pdf_file', 'supplementary_data', 'raw_data_file',
            'view_count', 'download_count', 'co_authors',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'view_count', 'download_count', 'created_at', 'updated_at'
        ]
    
    def to_representation(self, instance):
        """Override to apply JWT tier-based field masking."""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        if not request or not request.user.is_authenticated:
            # Unauthenticated: only abstract visible
            data['pdf_file'] = None
            data['supplementary_data'] = None
            data['raw_data_file'] = None
        else:
            # Check JWT tier
            user_tier = getattr(request.user.researcher_profile, 'tier', 'basic')
            
            if user_tier == 'basic':
                # Basic: abstract and PDF only
                data['raw_data_file'] = None
            elif user_tier == 'premium':
                # Premium: everything except raw data (unless explicit permission)
                if not self.has_raw_data_access(request.user, instance):
                    data['raw_data_file'] = None
            # Admin: full access (all fields remain visible)
        
        return data
    
    @staticmethod
    def has_raw_data_access(user, paper):
        """Check if user has explicit permission for raw data."""
        return AccessPermission.objects.filter(
            paper=paper,
            reviewer=user,
            permission_type__in=['view_raw_data', 'download_raw_data'],
            is_active=True
        ).exists()


class DatasetSerializer(serializers.ModelSerializer):
    """Serializer for Dataset with conditional field masking."""
    researcher = ResearcherProfileSerializer(read_only=True)
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'researcher', 'paper', 'title', 'description',
            'file_format', 'file_size', 'status', 'visibility',
            'data_file', 'creation_date', 'version',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'creation_date', 'created_at', 'updated_at'
        ]
    
    def to_representation(self, instance):
        """Apply access control based on JWT tier."""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        if not request or not request.user.is_authenticated:
            data['data_file'] = None
        else:
            user_tier = getattr(request.user.researcher_profile, 'tier', 'basic')
            if user_tier == 'basic':
                data['data_file'] = None
        
        return data


class AccessPermissionSerializer(serializers.ModelSerializer):
    """Serializer for AccessPermission."""
    class Meta:
        model = AccessPermission
        fields = [
            'id', 'paper', 'dataset', 'reviewer', 'permission_type',
            'granted_by', 'expires_at', 'granted_at', 'revoked_at', 'is_active'
        ]
        read_only_fields = ['id', 'granted_at', 'revoked_at']


class FileAccessLogSerializer(serializers.ModelSerializer):
    """Serializer for FileAccessLog."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = FileAccessLog
        fields = [
            'id', 'user', 'paper', 'dataset', 'access_type',
            'ip_address', 'accessed_at'
        ]
        read_only_fields = ['id', 'accessed_at']


class CitationSerializer(serializers.Serializer):
    """Serializer for citation generation (not a model)."""
    paper_id = serializers.UUIDField()
    format = serializers.ChoiceField(choices=['bibtex', 'apa', 'mla', 'chicago'])
    
    def to_representation(self, instance):
        """Generate citation in requested format."""
        # This would integrate with external citation engines
        return {
            'citation': 'Generated citation would appear here',
            'format': instance['format']
        }
