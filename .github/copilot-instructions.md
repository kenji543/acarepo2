# Secure Academic Research & Portfolio Repository
# Copilot Instructions

## Project Structure

This is a Django-based academic portfolio management system with the following architecture:

### Core Applications
- **portfolio**: Core portfolio models (ResearcherProfile, ResearchPaper, Dataset, AccessPermission)
- **api**: Django REST Framework API with tiered access control
- **auth_service**: JWT authentication with token blacklisting
- **security**: Threat detection, honeypots, and access control

### Key Features
1. **Tiered Access Control**: Private, Peer Review, Institution, Public
2. **Anti-IDOR Protection**: Object-level permissions on all models
3. **JWT Authentication**: Field-level masking based on user tier
4. **File Management**: Cloudinary integration for PDF and dataset storage
5. **Audit Logging**: Comprehensive access and event logging
6. **Security Hardening**: django-axes, rate-limiting, honeypots, threat detection

## Environment Setup

Required environment variables in `.env`:
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string (Supabase)
- `CLOUDINARY_*`: Cloudinary credentials
- `DEBUG`: Set to False in production

## Development Commands

```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Superuser
python manage.py createsuperuser

# Runserver
python manage.py runserver

# Security checks
python manage.py check --deploy
```

## API Testing

Use `postman_collection.json` for API testing with JWT authentication.

### Important Notes
1. Always use `Authorization: Bearer {access_token}` header
2. Rate limits: 10/hour for downloads, 1000/hour for authenticated API calls
3. All file access is logged and tracked
4. Never commit `.env` or credentials to version control

## Deployment

### Railway
- Configured with `railway.toml` and `Dockerfile`
- Requires Supabase PostgreSQL and Cloudinary credentials
- SAST scans run on deployment

### Local Docker
```bash
docker-compose up -d
```

## Security Best Practices

1. **Never bypass permission checks** - Always use permission classes
2. **Validate all user input** - Use Django forms and DRF serializers
3. **Log security events** - Use `audit_logs` and threat tracking
4. **Rotate JWT tokens** - Implement token refresh strategy
5. **Monitor threats** - Check `ThreatAlert` admin panel regularly

## Testing

Run tests with:
```bash
python manage.py test
coverage run --source='.' manage.py test
coverage report
```
