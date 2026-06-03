from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator, FileExtensionValidator
from cloudinary.models import CloudinaryField
import uuid


class ResearcherProfile(models.Model):
    """Extended user profile for academic researchers."""
    TIER_CHOICES = (
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('admin', 'Administrator'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='researcher_profile')
    bio = models.TextField(blank=True, null=True, help_text="Professional biography")
    institution = models.CharField(max_length=255, blank=True, help_text="University/Research Institution")
    department = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=100, blank=True, help_text="Job title/Position")
    orcid_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        default=None,
        help_text="ORCID identifier",
    )
    google_scholar = models.URLField(blank=True, validators=[URLValidator()])
    research_interests = models.TextField(blank=True, help_text="Comma-separated research areas")
    
    # Privacy and access tier
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='basic')
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Researcher Profile'
        verbose_name_plural = 'Researcher Profiles'
        indexes = [
            models.Index(fields=['user', 'tier']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.institution}"


class ResearchPaper(models.Model):
    """Research papers with full metadata and privacy controls."""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('peer_review', 'Under Peer Review'),
        ('archived', 'Archived'),
    )
    
    VISIBILITY_CHOICES = (
        ('private', 'Private - Only Owner'),
        ('peer_review', 'Peer Reviewers Only'),
        ('institution', 'Institution Members'),
        ('public', 'Public'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    researcher = models.ForeignKey(ResearcherProfile, on_delete=models.CASCADE, related_name='papers')
    
    # Paper metadata
    title = models.CharField(max_length=500)
    abstract = models.TextField(help_text="Research abstract - always visible")
    keywords = models.CharField(max_length=500, blank=True, help_text="Comma-separated keywords")
    publication_date = models.DateField(blank=True, null=True)
    doi = models.CharField(max_length=100, blank=True, unique=True, help_text="Digital Object Identifier")
    
    # Access control
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    
    # File storage
    pdf_file = CloudinaryField(
        'paper_pdf',
        resource_type='raw',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="Full research paper PDF"
    )
    supplementary_data = CloudinaryField(
        'supplementary',
        resource_type='raw',
        null=True,
        blank=True,
        help_text="Supplementary materials/datasets"
    )
    
    # Raw data (highly sensitive - restricted access)
    raw_data_file = CloudinaryField(
        'raw_data',
        resource_type='raw',
        null=True,
        blank=True,
        help_text="Raw experimental data - restricted access"
    )
    
    # Citation and tracking
    view_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Research Paper'
        verbose_name_plural = 'Research Papers'
        ordering = ['-publication_date', '-created_at']
        indexes = [
            models.Index(fields=['researcher', 'visibility', 'status']),
            models.Index(fields=['doi']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.researcher.user.username}"
    
    def get_author_name(self):
        """Get primary author name from researcher profile."""
        return self.researcher.user.get_full_name() or self.researcher.user.username
    
    def get_publication_year(self):
        """Get publication year from date."""
        if self.publication_date:
            return self.publication_date.year
        return self.created_at.year
    
    def get_journal_info(self):
        """Get journal/publisher info - can be extended with a model field."""
        return "Academic Research Portfolio"
    
    def generate_apa_citation(self):
        """Generate APA formatted citation."""
        author = self.get_author_name()
        year = self.get_publication_year()
        title = self.title
        journal = self.get_journal_info()
        
        citation = f"{author} ({year}). {title}. {journal}."
        if self.doi:
            citation += f" https://doi.org/{self.doi}"
        return citation
    
    def generate_mla_citation(self):
        """Generate MLA formatted citation."""
        author = self.get_author_name()
        title = self.title
        journal = self.get_journal_info()
        year = self.get_publication_year()
        
        citation = f"{author}. \"{title}.\" {journal}, {year}."
        if self.doi:
            citation += f" Web. https://doi.org/{self.doi}"
        return citation
    
    def generate_bibtex_citation(self):
        """Generate BibTeX formatted citation."""
        author = self.get_author_name()
        title = self.title
        year = self.get_publication_year()
        
        # Use DOI as key if available, otherwise use author + year
        key = self.doi.replace("/", "_") if self.doi else f"{author.split()[-1]}{year}"
        
        citation = f"@article{{{key},\n"
        citation += f"  author = {{{author}}},\n"
        citation += f"  title = {{{title}}},\n"
        citation += f"  year = {{{year}}}"
        if self.doi:
            citation += f",\n  doi = {{{self.doi}}}"
        citation += "\n}"
        
        return citation
    
    def get_all_citations(self):
        """Return dictionary with all citation formats."""
        return {
            'apa': self.generate_apa_citation(),
            'mla': self.generate_mla_citation(),
            'bibtex': self.generate_bibtex_citation(),
        }
    
    @property
    def thumbnail_url(self):
        """Generate Cloudinary thumbnail URL for PDF preview.
        
        Converts PDF to JPG thumbnail using Cloudinary's transformation API.
        Example: pdf_file URL becomes thumbnail with page 1, scaled to 120x160px.
        """
        if not self.pdf_file:
            return None
        
        try:
            pdf_url = str(self.pdf_file.url)
            # Cloudinary URL format: https://res.cloudinary.com/{cloud_name}/{resource_type}/upload/{public_id}
            # Transform to: https://res.cloudinary.com/{cloud_name}/{resource_type}/upload/c_pad,w_120,h_160,pg_1/f_jpg/{public_id}
            
            # Split URL to inject transformation parameters
            if 'upload/' in pdf_url:
                # Insert transformation parameters before the public_id
                parts = pdf_url.split('upload/')
                transformation = 'c_pad,w_120,h_160,pg_1/f_jpg/'
                thumbnail = parts[0] + 'upload/' + transformation + parts[1]
                return thumbnail
        except Exception as e:
            import logging
            logging.error(f"Error generating thumbnail URL for paper {self.id}: {e}")
        
        return None


class CoAuthor(models.Model):
    """Co-authors for research papers with order tracking."""
    paper = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE, related_name='co_authors')
    author_name = models.CharField(max_length=255)
    author_email = models.EmailField(blank=True)
    author_institution = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(help_text="Author order in publication")
    
    class Meta:
        verbose_name = 'Co-Author'
        verbose_name_plural = 'Co-Authors'
        ordering = ['paper', 'order']
        unique_together = ['paper', 'order']
    
    def __str__(self):
        return f"{self.author_name} - {self.paper.title}"


class Dataset(models.Model):
    """Datasets associated with research papers."""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('deprecated', 'Deprecated'),
    )
    
    VISIBILITY_CHOICES = (
        ('private', 'Private - Only Owner'),
        ('peer_review', 'Peer Reviewers Only'),
        ('public', 'Public'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    researcher = models.ForeignKey(ResearcherProfile, on_delete=models.CASCADE, related_name='datasets')
    paper = models.ForeignKey(ResearchPaper, on_delete=models.SET_NULL, null=True, blank=True, related_name='datasets')
    
    # Dataset metadata
    title = models.CharField(max_length=500)
    description = models.TextField()
    file_format = models.CharField(max_length=50, help_text="e.g., CSV, JSON, HDF5, NetCDF")
    file_size = models.BigIntegerField(help_text="File size in bytes")
    
    # Access control
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    
    # File storage
    data_file = CloudinaryField(
        'dataset',
        resource_type='raw',
        help_text="Uploaded dataset file"
    )
    
    # Metadata
    creation_date = models.DateField(auto_now_add=True)
    version = models.CharField(max_length=20, default='1.0')
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'
        ordering = ['-creation_date', '-created_at']
        indexes = [
            models.Index(fields=['researcher', 'visibility']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.researcher.user.username}"


class AccessPermission(models.Model):
    """Fine-grained access control for papers and datasets."""
    PERMISSION_TYPES = (
        ('view_abstract', 'View Abstract Only'),
        ('view_full', 'View Full Paper'),
        ('download', 'Download Paper'),
        ('view_raw_data', 'View Raw Data'),
        ('download_raw_data', 'Download Raw Data'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paper = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE, related_name='access_permissions', null=True, blank=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='access_permissions', null=True, blank=True)
    
    # Grantee
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paper_access_permissions')
    
    # Permission details
    permission_type = models.CharField(max_length=50, choices=PERMISSION_TYPES)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='permissions_granted')
    
    # Time-based access
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Leave blank for permanent access")
    
    # Audit fields
    granted_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Access Permission'
        verbose_name_plural = 'Access Permissions'
        unique_together = ['paper', 'dataset', 'reviewer', 'permission_type']
        indexes = [
            models.Index(fields=['reviewer', 'is_active']),
            models.Index(fields=['granted_at']),
        ]
    
    def __str__(self):
        resource = self.paper.title if self.paper else self.dataset.title
        return f"{self.reviewer.username} - {self.permission_type} - {resource}"


class FileAccessLog(models.Model):
    """Audit log for file access - tracks all downloads and views."""
    ACCESS_TYPES = (
        ('view', 'View'),
        ('download', 'Download'),
        ('preview', 'Preview'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='file_access_logs')
    paper = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE, null=True, blank=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True, blank=True)
    
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    accessed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'File Access Log'
        verbose_name_plural = 'File Access Logs'
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['user', 'accessed_at']),
            models.Index(fields=['paper', 'accessed_at']),
            models.Index(fields=['dataset', 'accessed_at']),
        ]
    
    def __str__(self):
        resource = f"Paper: {self.paper.title}" if self.paper else f"Dataset: {self.dataset.title}"
        return f"{self.user.username} - {self.access_type} - {resource}"
