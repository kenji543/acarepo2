# Secure Academic Research & Portfolio Repository

A comprehensive Django-based digital portfolio management system enabling university faculty to upload, manage, and showcase publications, datasets, and professional credentials with tiered data-privacy controls.

## 🎯 Core Features

### 1. **Academic Portfolio Management**
- Faculty portfolio creation and management
- Research paper publication with metadata (DOI, keywords, abstract)
- Dataset management with version control
- Co-author management with ordered attribution
- ORCID and Google Scholar integration

### 2. **Tiered Access Control**
- **Private**: Only owner access
- **Peer Review**: Authorized reviewers only
- **Institution**: Institution members
- **Public**: General public access

### 3. **Advanced Security**
- **JWT Authentication**: Field-level data masking based on user tier
- **Anti-IDOR Protection**: Object-level permissions with Django ORM validation
- **Rate Limiting**: 10/hour for document downloads, 100/hour for anonymous users
- **Brute-Force Protection**: `django-axes` with 5-attempt lockout (15-minute cooloff)
- **Honeypot Fields**: Automated attack detection and logging
- **Threat Intelligence**: Comprehensive threat detection and alerting system
- **IP Blacklisting**: Dynamic IP blocking for suspicious activity

### 4. **File Management**
- **Cloudinary Integration**: PDF and dataset storage and delivery
- **Raw Data Protection**: Restricted access to sensitive experimental data
- **Supplementary Materials**: Support for additional research materials
- **Download Tracking**: Audit logs for all file access and downloads

### 5. **API Capabilities**
- **RESTful Endpoints**: Django REST Framework with comprehensive API
- **Citation Generation**: BibTeX, APA, MLA, Chicago formats
- **Advanced Filtering**: Full-text search, institutional filters
- **Pagination**: Efficient data retrieval with configurable page sizes
- **Audit Logging**: Complete access trail for compliance

### 6. **Audit & Compliance**
- **File Access Logs**: IP, user agent, timestamp tracking
- **Login/Logout Audit**: Comprehensive authentication event logging
- **Threat Monitoring**: Real-time detection and alerting
- **Permission Tracking**: Fine-grained access permission audit trail

## 📋 Tech Stack

- **Backend Framework**: Django 4.2.13
- **API Framework**: Django REST Framework 3.14.0
- **Database**: PostgreSQL (via Supabase)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Cloud Storage**: Cloudinary
- **Security**: django-axes, django-ratelimit
- **Deployment**: Railway with Docker
- **Python Version**: 3.11

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Cloudinary account
- Git

### Local Development Setup

1. **Clone and setup environment**
   ```bash
   git clone <repository-url>
   cd AcademicRep0
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase and Cloudinary credentials
   ```

4. **Initialize database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run development server**
   ```bash
   python manage.py runserver
   ```

Access the application at `http://localhost:8000`

### Using Docker Compose

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database on port 5432
- Redis cache on port 6379
- Django application on port 8000

## 📚 API Documentation

### Authentication

**Login Endpoint**
```
POST /auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "tier": "premium",
  "institution": "Harvard University"
}
```

### Key Endpoints

#### Researcher Profiles
- `GET /api/researchers/` - List all public researcher profiles
- `GET /api/researchers/{id}/` - Get specific researcher profile
- `GET /api/researchers/my-profile/` - Get current user's profile (requires auth)
- `POST /api/researchers/` - Create new researcher profile (auth required)

#### Research Papers
- `GET /api/papers/` - List papers (access controlled by visibility)
- `POST /api/papers/` - Upload new paper (auth required)
- `GET /api/papers/{id}/` - Get paper details
- `GET /api/papers/{id}/download/` - Download paper PDF (rate limited)
- `GET /api/papers/{id}/citations/` - Generate citations
  - Query param: `format=bibtex|apa|mla|chicago`

#### Datasets
- `GET /api/datasets/` - List datasets
- `POST /api/datasets/` - Upload dataset
- `GET /api/datasets/{id}/` - Get dataset details

#### Access Permissions
- `GET /api/permissions/` - List access permissions
- `POST /api/permissions/` - Grant access permission
- `DELETE /api/permissions/{id}/` - Revoke permission

#### Audit Logs
- `GET /api/audit-logs/` - Retrieve access logs for own papers (read-only)

### JWT Token Structure

Access tokens include:
- `user_id`: User identifier
- `tier`: User tier (basic, premium, admin)
- `institution`: User's institution
- `exp`: Token expiration time
- `iat`: Token issued time

## 🔐 Security Features

### Anti-IDOR Protection
All endpoints enforce object-level permissions:
```python
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.researcher.user == request.user
```

### Rate Limiting
- **Document Downloads**: 10 requests/hour per user
- **API Requests**: 1000/hour authenticated, 100/hour anonymous
- Configurable via `REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']`

### Brute-Force Protection (django-axes)
- Lockout after 5 failed login attempts
- 15-minute lockout duration
- IP-based and user-based tracking
- Automatic unlock after cooloff period

### Honeypot Detection
- Transparent honeypot fields in forms
- Automatic detection of automated submissions
- Logged as threat events for analysis

## 📊 Data Privacy Tiers

### Basic Tier
- View public papers' abstracts
- Download PDFs (if public)
- No raw data access

### Premium Tier
- All basic features
- View full papers (if shared)
- Limited raw data access (with explicit permission)
- Extended citation formats

### Admin Tier
- Full system access
- View all papers and data
- Raw data access without restrictions
- User and permission management

## 🛠️ Admin Interface

Access Django admin at `/admin/` with superuser credentials:

**Available Management Panels**:
- Researcher Profiles
- Research Papers & Co-Authors
- Datasets
- Access Permissions
- File Access Logs
- Authentication Events
- Security Alerts
- Threat Intelligence
- IP Whitelist/Blacklist

## 🚢 Production Deployment

### Railway Setup

1. **Connect Repository**
   ```bash
   railway link
   ```

2. **Set Environment Variables**
   ```bash
   railway variables
   ```
   Required variables:
   - `SECRET_KEY`
   - `DATABASE_URL` (Supabase)
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

3. **Deploy**
   ```bash
   git push  # Triggers automatic deployment
   ```

### Pre-Deployment Security Checks

```bash
# Run Django security checks
python manage.py check --deploy

# Execute SAST scans
pip-audit  # Check for vulnerable dependencies
bandit -r . # Check code security issues

# Generate security report
bandit -r . -f json -o security-report.json
```

## 📋 Database Schema

### Core Models
- **ResearcherProfile**: Extended user profiles with institution/tier info
- **ResearchPaper**: Research publications with file storage
- **CoAuthor**: Author attribution with ordering
- **Dataset**: Experimental data with privacy controls
- **AccessPermission**: Fine-grained permission management
- **FileAccessLog**: Comprehensive audit trail

### Security Models
- **ThreatAlert**: Security event tracking
- **HoneypotField**: Automated attack detection
- **IPBlacklist/Whitelist**: IP-based access control
- **TokenBlacklist**: JWT token revocation tracking
- **AuditLog**: Authentication and security events

## 📝 Postman Collection

A comprehensive Postman collection is provided: `postman_collection.json`

**Import Instructions**:
1. Open Postman
2. Click "Import" → "Select File"
3. Choose `postman_collection.json`
4. Set base URL: `http://localhost:8000` (local) or your Railway domain
5. Obtain JWT token from Login endpoint
6. Use token in Authorization header for protected endpoints

## 🔄 CI/CD Pipeline

GitHub Actions workflow included for:
- Running Django tests
- SAST security scanning (Bandit, pip-audit)
- Linting (flake8)
- Building Docker image
- Pushing to container registry

## 📖 API Response Examples

### Successful Paper List Response (Tiered Masking)
```json
{
  "count": 45,
  "next": "http://api.example.com/papers/?page=2",
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Novel Approaches in Quantum Computing",
      "abstract": "Abstract text always visible...",
      "pdf_file": "https://res.cloudinary.com/...",  // Visible to authenticated users
      "raw_data_file": "https://res.cloudinary.com/...",  // Only for premium/admin
      "visibility": "peer_review",
      "researcher": {...}
    }
  ]
}
```

### Unauthorized Response
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## 🧪 Testing

Run tests:
```bash
python manage.py test
```

Test coverage:
```bash
coverage run --source='.' manage.py test
coverage report
```

## 📞 Support & Documentation

- **Django Documentation**: https://docs.djangoproject.com/
- **DRF Documentation**: https://www.django-rest-framework.org/
- **Supabase Documentation**: https://supabase.com/docs
- **Cloudinary Documentation**: https://cloudinary.com/documentation

## 📄 License

[Specify your license here]

## 👥 Contributors

Academic Research Team - 2026

---

**Last Updated**: June 2, 2026  
**Status**: Production Ready  
**Version**: 1.0.0
