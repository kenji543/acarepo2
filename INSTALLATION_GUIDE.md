# Installation & Deployment Guide

## Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Cloudinary account (free tier available)
- Supabase account (free tier available)
- Git

## Local Development Setup

### 1. Clone Repository
```bash
cd AcademicRep0
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
cp .env.example .env
```

Edit `.env` and fill in:
- `SECRET_KEY`: Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DATABASE_URL`: Your Supabase PostgreSQL URL
- `CLOUDINARY_*`: Your Cloudinary credentials

### 5. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Create Researcher Profile
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from portfolio.models import ResearcherProfile
>>> user = User.objects.get(username='admin')
>>> ResearcherProfile.objects.create(user=user, tier='admin', institution='Your University')
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit:
- Application: `http://localhost:8000`
- Admin: `http://localhost:8000/admin`
- API: `http://localhost:8000/api`

## Using Docker

### Build & Run
```bash
docker-compose up -d
```

Access at `http://localhost:8000`

### Stop Services
```bash
docker-compose down
```

## Production Deployment on Railway

### 1. Connect Repository
```bash
npm install -g railway
railway login
railway link
```

### 2. Set Environment Variables
```bash
railway variables
```

Required:
- `SECRET_KEY`
- `DATABASE_URL` (Supabase)
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`
- `DEBUG=False`
- `ALLOWED_HOSTS=yourdomain.com`

### 3. Deploy
```bash
git push  # Automatic deployment via Railway
```

### 4. Verify Deployment
```bash
railway logs
railway logs --service web
```

## Post-Deployment Checklist

- [ ] Verify application is running: `https://your-domain.com/health`
- [ ] Check admin access: `https://your-domain.com/admin`
- [ ] Run security checks: `python manage.py check --deploy`
- [ ] Run SAST scans: `bandit -r . && pip-audit`
- [ ] Review ThreatAlert table in Django admin
- [ ] Set up email notifications (optional)
- [ ] Configure SSL/TLS certificate
- [ ] Enable HSTS headers
- [ ] Set up monitoring and alerting

## Troubleshooting

### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -U user -h host -d database_name

# Check Django ORM connection
python manage.py dbshell
```

### Cloudinary Upload Issues
```bash
# Verify credentials
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CLOUDINARY_STORAGE)
```

### Static Files Not Loading
```bash
# Regenerate static files
python manage.py collectstatic --noinput --clear
```

### Permission Denied Errors
```bash
# Check file permissions
ls -la logs/
chmod 755 logs/

# Reset database permissions
python manage.py migrate
```

## Security Hardening

### HTTPS/TLS
Configure in `.env`:
```
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

### Database
- Use strong passwords
- Enable SSL for database connections
- Restrict access to application server only

### Cloudinary
- Use restricted API keys
- Enable signed URLs
- Limit upload folders

### Admin Panel
- Change default URL from `/admin/` to `/management/` (optional)
- Enable IP whitelisting
- Use strong admin password

## Monitoring & Maintenance

### Daily Tasks
```bash
# Check security alerts
python manage.py audit_report

# Monitor threat detection
# Visit Django admin → Security → Threat Alerts
```

### Weekly Tasks
```bash
# Run full security audit
bandit -r . -f json -o security-audit.json
pip-audit --desc

# Review access logs
# Visit Django admin → Portfolio → File Access Logs
```

### Monthly Tasks
```bash
# Clean up expired data
python manage.py security_maintenance

# Review user activity
# Via Django admin audit logs
```

## Backup & Restore

### Backup Database
```bash
# Using Supabase dashboard or:
pg_dump -U user -h host database_name > backup.sql
```

### Backup Cloudinary
```bash
# Export all assets
curl -s "https://api.cloudinary.com/v1_1/your-cloud/resources/raw?type=list&max_results=500&prefix=papers" \
  --user api_key:api_secret > cloudinary_backup.json
```

## Support & Troubleshooting

For issues:
1. Check logs: `logs/academic_portfolio.log`
2. Review Django error page (if DEBUG=True locally)
3. Check Railway logs: `railway logs`
4. Consult [Django Docs](https://docs.djangoproject.com/)
5. Review [DRF Docs](https://www.django-rest-framework.org/)

## Performance Optimization

### Database
- Add indexes for frequently queried fields (already done)
- Use `select_related()` and `prefetch_related()` in queries
- Monitor slow queries

### Caching
- Redis integration ready in `docker-compose.yml`
- Configure Django cache in settings for production

### Static Files
- Enable Cloudinary for static file storage
- Use WhiteNoise for efficient serving
- Set cache headers appropriately
