from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from portfolio.models import (
    ResearcherProfile, ResearchPaper, Dataset,
    AccessPermission, FileAccessLog
)
from .serializers import (
    ResearcherProfileSerializer, ResearchPaperSerializer,
    DatasetSerializer, AccessPermissionSerializer,
    FileAccessLogSerializer
)
from .permissions import (
    IsOwnerOrReadOnly, IsReviewerOrOwner, CanDownloadDocument
)
import logging

logger = logging.getLogger('django.security')


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ResearcherProfileViewSet(viewsets.ModelViewSet):
    """API endpoints for researcher profiles."""
    queryset = ResearcherProfile.objects.select_related('user')
    serializer_class = ResearcherProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tier', 'institution']
    search_fields = ['user__username', 'institution', 'orcid_id']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_profile(self, request):
        """Get current user's profile."""
        profile, _ = ResearcherProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def papers(self, request, pk=None):
        """Get all papers for a researcher."""
        researcher = self.get_object()
        papers = researcher.papers.filter(visibility='public', status='published')
        serializer = ResearchPaperSerializer(papers, many=True, context={'request': request})
        return Response(serializer.data)


class ResearchPaperViewSet(viewsets.ModelViewSet):
    """API endpoints for research papers with tiered access control."""
    queryset = ResearchPaper.objects.select_related('researcher__user').prefetch_related('co_authors')
    serializer_class = ResearchPaperSerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'visibility', 'researcher']
    search_fields = ['title', 'abstract', 'keywords', 'doi']
    ordering_fields = ['publication_date', 'created_at', 'view_count']
    ordering = ['-publication_date']
    
    def get_queryset(self):
        """Filter papers based on visibility and user authentication."""
        queryset = super().get_queryset()
        
        if not self.request.user.is_authenticated:
            # Unauthenticated: only public papers
            return queryset.filter(visibility='public', status='published')
        
        user_tier = getattr(self.request.user.researcher_profile, 'tier', 'basic')
        
        if user_tier == 'admin':
            # Admin: all papers
            return queryset
        elif user_tier == 'premium':
            # Premium: public + papers they have access to
            accessible_papers = AccessPermission.objects.filter(
                reviewer=self.request.user,
                is_active=True
            ).values_list('paper_id', flat=True)
            return queryset.filter(
                Q(visibility='public') | Q(id__in=accessible_papers) | Q(researcher__user=self.request.user)
            )
        else:
            # Basic: public + own papers
            return queryset.filter(
                Q(visibility='public') | Q(researcher__user=self.request.user)
            )
    
    def perform_create(self, serializer):
        """Assign paper to current user's researcher profile."""
        researcher, _ = ResearcherProfile.objects.get_or_create(user=self.request.user)
        serializer.save(researcher=researcher)
    
    @method_decorator(ratelimit(key='user', rate='10/h', method='GET', block=True))
    @action(detail=True, methods=['get'], permission_classes=[CanDownloadDocument])
    def download(self, request, pk=None):
        """Download paper PDF with rate limiting."""
        paper = self.get_object()
        
        # Log download
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        FileAccessLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            paper=paper,
            access_type='download',
            ip_address=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Increment download count
        paper.download_count += 1
        paper.save(update_fields=['download_count'])
        
        return Response({
            'download_url': paper.pdf_file.url if paper.pdf_file else None,
            'filename': f"{paper.title.replace(' ', '_')}.pdf"
        })
    
    @action(detail=True, methods=['get'])
    def citations(self, request, pk=None):
        """Generate citations in various formats."""
        paper = self.get_object()
        format_type = request.query_params.get('format', 'bibtex')
        
        # This would integrate with external citation services
        citations = {
            'bibtex': self._generate_bibtex(paper),
            'apa': self._generate_apa(paper),
            'mla': self._generate_mla(paper),
            'chicago': self._generate_chicago(paper),
        }
        
        return Response({'citations': citations.get(format_type, citations['bibtex'])})
    
    @staticmethod
    def _generate_bibtex(paper):
        """Generate BibTeX citation."""
        return f"""@article{{{paper.doi or paper.id},
            title={{{paper.title}}},
            author={{{', '.join([a.author_name for a in paper.co_authors.all()])}}},
            year={{{paper.publication_date.year if paper.publication_date else 'n.d.'}}},
            doi={{{paper.doi}}}
        }}"""
    
    @staticmethod
    def _generate_apa(paper):
        """Generate APA citation."""
        authors = ', '.join([a.author_name for a in paper.co_authors.all()])
        year = paper.publication_date.year if paper.publication_date else 'n.d.'
        return f"{authors} ({year}). {paper.title}."
    
    @staticmethod
    def _generate_mla(paper):
        """Generate MLA citation."""
        authors = ', '.join([a.author_name for a in paper.co_authors.all()])
        year = paper.publication_date.year if paper.publication_date else 'n.d.'
        return f"{authors}. \"{paper.title}.\" {year}."
    
    @staticmethod
    def _generate_chicago(paper):
        """Generate Chicago citation."""
        authors = ', '.join([a.author_name for a in paper.co_authors.all()])
        year = paper.publication_date.year if paper.publication_date else 'n.d.'
        return f"{authors}. {paper.title}. {year}."


class DatasetViewSet(viewsets.ModelViewSet):
    """API endpoints for datasets."""
    queryset = Dataset.objects.select_related('researcher__user', 'paper')
    serializer_class = DatasetSerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'visibility', 'file_format', 'researcher']
    search_fields = ['title', 'description']
    
    def get_queryset(self):
        """Filter datasets based on visibility."""
        queryset = super().get_queryset()
        
        if not self.request.user.is_authenticated:
            return queryset.filter(visibility='public')
        
        user_tier = getattr(self.request.user.researcher_profile, 'tier', 'basic')
        
        if user_tier == 'admin':
            return queryset
        elif user_tier == 'premium':
            accessible = AccessPermission.objects.filter(
                reviewer=self.request.user,
                is_active=True
            ).values_list('dataset_id', flat=True)
            return queryset.filter(
                Q(visibility='public') | Q(id__in=accessible) | Q(researcher__user=self.request.user)
            )
        else:
            return queryset.filter(
                Q(visibility='public') | Q(researcher__user=self.request.user)
            )
    
    def perform_create(self, serializer):
        researcher, _ = ResearcherProfile.objects.get_or_create(user=self.request.user)
        serializer.save(researcher=researcher)


class AccessPermissionViewSet(viewsets.ModelViewSet):
    """API endpoints for managing access permissions."""
    queryset = AccessPermission.objects.select_related('paper', 'dataset', 'reviewer', 'granted_by')
    serializer_class = AccessPermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsReviewerOrOwner]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Only show permissions user is involved with."""
        if self.request.user.is_staff:
            return super().get_queryset()
        
        return AccessPermission.objects.filter(
            Q(granted_by=self.request.user) | Q(reviewer=self.request.user)
        )
    
    def perform_create(self, serializer):
        serializer.save(granted_by=self.request.user)


class FileAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoints for audit logs (read-only)."""
    queryset = FileAccessLog.objects.select_related('user', 'paper', 'dataset')
    serializer_class = FileAccessLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Users can only see logs for their own papers."""
        user_papers = ResearchPaper.objects.filter(researcher__user=self.request.user)
        user_datasets = Dataset.objects.filter(researcher__user=self.request.user)
        
        return FileAccessLog.objects.filter(
            Q(paper__in=user_papers) | Q(dataset__in=user_datasets)
        )
