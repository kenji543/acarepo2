"""
Quick reference for developers working on the Academic Portfolio Repository.
"""

# API ENDPOINTS QUICK REFERENCE

## Authentication
- POST   /auth/login/               - User login (returns access & refresh tokens)
- POST   /auth/refresh/             - Refresh access token
- POST   /auth/register/            - Register new user
- POST   /auth/logout/              - Logout & blacklist token

## Researcher Profiles
- GET    /api/researchers/          - List all public profiles
- GET    /api/researchers/{id}/     - Get specific researcher
- GET    /api/researchers/my-profile/ - Get current user's profile (auth required)
- POST   /api/researchers/          - Create profile
- PUT    /api/researchers/{id}/     - Update profile

## Research Papers
- GET    /api/papers/               - List papers (access-controlled)
- POST   /api/papers/               - Upload paper (auth required)
- GET    /api/papers/{id}/          - Get paper details
- GET    /api/papers/{id}/download/ - Download PDF (rate-limited)
- GET    /api/papers/{id}/citations/ - Generate citations (param: format=bibtex/apa/mla/chicago)
- PUT    /api/papers/{id}/          - Update paper
- DELETE /api/papers/{id}/          - Delete paper

## Datasets
- GET    /api/datasets/             - List datasets
- POST   /api/datasets/             - Upload dataset
- GET    /api/datasets/{id}/        - Get dataset details

## Access Permissions
- GET    /api/permissions/          - List permissions
- POST   /api/permissions/          - Grant access
- DELETE /api/permissions/{id}/     - Revoke access

## Audit Logs
- GET    /api/audit-logs/           - View access logs (read-only)

# JWT TOKEN STRUCTURE

Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "token_type": "access",
  "exp": 1234567890,
  "iat": 1234567890,
  "user_id": 1,
  "username": "researcher@example.com",
  "tier": "premium",
  "institution": "MIT"
}

# PERMISSION TIERS

- basic: View abstracts, download public papers
- premium: All basic + view full papers (if shared), limited raw data access
- admin: Full system access, all content, all permissions

# RATE LIMITS

- Anonymous Users: 100 requests/hour
- Authenticated Users: 1000 requests/hour
- Paper Downloads: 10 downloads/hour per user
- Failed Login Attempts: 5 attempts before 15-minute lockout (django-axes)

# SECURITY FEATURES

1. Anti-IDOR: All endpoints check object-level permissions
2. JWT Masking: Fields hidden based on user tier
3. Rate Limiting: Per-endpoint and per-user throttling
4. Brute Force: django-axes with configurable lockout
5. Honeypots: Automated attack detection
6. Threat Monitoring: Real-time threat alerts
7. IP Blacklisting: Dynamic blocking for suspicious IPs
8. Audit Logging: Complete access trail

# ENVIRONMENT VARIABLES REQUIRED

DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host/db
CLOUDINARY_CLOUD_NAME=your-cloud
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# COMMON DJANGO COMMANDS

python manage.py migrate               - Run database migrations
python manage.py makemigrations        - Create migration files
python manage.py createsuperuser       - Create admin user
python manage.py runserver             - Start dev server
python manage.py test                  - Run tests
python manage.py check --deploy        - Security checks
python manage.py shell                 - Django shell
python manage.py collectstatic         - Collect static files

# MANAGEMENT COMMANDS

python manage.py detect_brute_force    - Detect and blacklist suspicious IPs
python manage.py audit_report          - Generate security audit report
python manage.py security_maintenance  - Clean up expired entries

# DEPLOYMENT CHECKLIST

- [ ] Set DEBUG=False
- [ ] Set SECURE_SSL_REDIRECT=True
- [ ] Set strong SECRET_KEY
- [ ] Configure Supabase/PostgreSQL
- [ ] Configure Cloudinary credentials
- [ ] Run migrations: python manage.py migrate
- [ ] Create superuser: python manage.py createsuperuser
- [ ] Collect static: python manage.py collectstatic --noinput
- [ ] Run security checks: python manage.py check --deploy
- [ ] Run SAST scans: bandit -r . && pip-audit
- [ ] Review ThreatAlert in admin panel
- [ ] Set up monitoring/logging

# TESTING

Run all tests:
  python manage.py test

Run specific app tests:
  python manage.py test portfolio
  python manage.py test api
  python manage.py test auth_service
  python manage.py test security

Run with coverage:
  coverage run --source='.' manage.py test
  coverage report
  coverage html  # generates htmlcov/index.html

# DEBUGGING TIPS

- Check logs in logs/academic_portfolio.log
- Monitor auth attempts in auth_service.AuditLog
- Review security events in security.ThreatAlert
- Check file access in portfolio.FileAccessLog
- Review permission errors with DRF browsable API

# USEFUL LINKS

Django: https://docs.djangoproject.com/
DRF: https://www.django-rest-framework.org/
Supabase: https://supabase.com/docs
Cloudinary: https://cloudinary.com/documentation
JWT: https://tools.ietf.org/html/rfc7519
