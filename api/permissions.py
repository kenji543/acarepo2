from rest_framework import permissions
from portfolio.models import AccessPermission, ResearchPaper, Dataset


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission to edit only own papers/datasets or read public content."""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is owner
        if hasattr(obj, 'researcher'):
            return obj.researcher.user == request.user
        
        return False


class IsReviewerOrOwner(permissions.BasePermission):
    """Permission for reviewer to access shared papers."""
    
    def has_object_permission(self, request, view, obj):
        # Owner can modify
        if obj.granted_by == request.user:
            return True
        
        # Reviewer can view
        if obj.reviewer == request.user:
            return request.method in permissions.SAFE_METHODS
        
        return False


class CanDownloadDocument(permissions.BasePermission):
    """Permission to download papers/datasets."""
    
    def has_object_permission(self, request, view, obj):
        # Check visibility
        if obj.visibility == 'public':
            return True
        
        # Owner can download own papers
        if hasattr(obj, 'researcher') and obj.researcher.user == request.user:
            return True
        
        # Check explicit permissions
        if request.user.is_authenticated:
            has_permission = AccessPermission.objects.filter(
                reviewer=request.user,
                is_active=True
            ).filter(
                (
                    (Q(paper=obj) if isinstance(obj, ResearchPaper) else Q(dataset=obj))
                    & Q(permission_type__in=['download', 'download_raw_data'])
                ) |
                Q(expires_at__isnull=True) |
                Q(expires_at__gte=timezone.now())
            ).exists()
            
            return has_permission
        
        return False


class IsPaperOwner(permissions.BasePermission):
    """Check if user owns the paper."""
    
    def has_object_permission(self, request, view, obj):
        return obj.researcher.user == request.user


from django.db.models import Q
from django.utils import timezone
