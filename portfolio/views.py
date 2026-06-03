from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView
from django.db.models import Q, Sum
from django_ratelimit.decorators import ratelimit
from .models import ResearchPaper, Dataset, ResearcherProfile, FileAccessLog
from .forms import ResearchPaperForm
import logging

logger = logging.getLogger('django.security')


@login_required
def researcher_dashboard(request):
    """Dashboard for researchers to manage their portfolio."""
    researcher_profile, _ = ResearcherProfile.objects.get_or_create(
        user=request.user,
        defaults={"orcid_id": None},
    )
    
    papers_qs = researcher_profile.papers.all()
    aggregates = papers_qs.aggregate(
        total_views=Sum('view_count'),
        total_downloads=Sum('download_count'),
    )

    context = {
        'researcher': researcher_profile,
        'papers': papers_qs,
        'datasets': researcher_profile.datasets.all(),
        'total_views': aggregates['total_views'] or 0,
        'total_downloads': aggregates['total_downloads'] or 0,
        'recent_access': FileAccessLog.objects.filter(
            paper__researcher=researcher_profile
        ).select_related('user', 'paper').order_by('-accessed_at')[:10],
    }
    return render(request, 'portfolio/dashboard.html', context)


class PortfolioListView(ListView):
    """Public portfolio listing with filtering."""
    model = ResearchPaper
    template_name = 'portfolio/portfolio_list.html'
    context_object_name = 'papers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ResearchPaper.objects.filter(visibility='public', status='published')
        
        # Search filtering
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(abstract__icontains=search_query) |
                Q(keywords__icontains=search_query)
            )
        
        # Filter by institution
        institution = self.request.GET.get('institution')
        if institution:
            queryset = queryset.filter(researcher__institution=institution)
        
        return queryset.select_related('researcher__user').prefetch_related('co_authors')

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['portfolio/partials/paper_grid.html']
        return [self.template_name]


class PaperDetailView(DetailView):
    """Detailed view of a research paper with access control."""
    model = ResearchPaper
    template_name = 'portfolio/paper_detail.html'
    context_object_name = 'paper'
    
    def get_object(self, queryset=None):
        paper = super().get_object(queryset)
        
        # Check visibility permissions
        if paper.visibility == 'private' and (not self.request.user.is_authenticated or 
                                              self.request.user != paper.researcher.user):
            self.handle_no_permission()
        
        # Log access
        ip = self.get_client_ip()
        FileAccessLog.objects.create(
            user=self.request.user if self.request.user.is_authenticated else None,
            paper=paper,
            access_type='view',
            ip_address=ip,
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Increment view count
        paper.view_count += 1
        paper.save(update_fields=['view_count'])
        
        return paper
    
    def get_client_ip(self):
        """Extract client IP from request."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


@ratelimit(key='user', rate='10/h', method='GET', block=True)
@login_required
def download_paper(request, paper_id):
    """Download paper PDF with rate limiting and access control."""
    paper = get_object_or_404(ResearchPaper, id=paper_id)
    
    # Check permissions
    if paper.visibility == 'private' and request.user != paper.researcher.user:
        logger.warning(f"Unauthorized download attempt by {request.user.username} for paper {paper_id}")
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Log download
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
    FileAccessLog.objects.create(
        user=request.user,
        paper=paper,
        access_type='download',
        ip_address=ip,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Increment download count
    paper.download_count += 1
    paper.save(update_fields=['download_count'])
    
    # Return Cloudinary file
    if paper.pdf_file:
        return redirect(paper.pdf_file.url)
    
    return JsonResponse({'error': 'File not found'}, status=404)


@login_required
def create_paper(request):
    """Create new research paper."""
    if not getattr(settings, "CLOUDINARY_CONFIGURED", False):
        messages.error(
            request,
            "File uploads are unavailable: Cloudinary credentials are not configured. "
            "Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET "
            "in your deployment environment.",
        )
        return redirect("dashboard")

    if request.method == 'POST':
        form = ResearchPaperForm(request.POST, request.FILES)
        if form.is_valid():
            researcher = ResearcherProfile.objects.get(user=request.user)
            paper = form.save(commit=False)
            paper.researcher = researcher
            paper.save()
            return redirect('paper_detail', pk=paper.id)
    else:
        form = ResearchPaperForm()
    
    return render(request, 'portfolio/paper_form.html', {'form': form})


def get_client_ip(request):
    """Utility to get client IP."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
