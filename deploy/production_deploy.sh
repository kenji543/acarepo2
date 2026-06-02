#!/bin/bash
# Production deployment script for Railway

# Exit on error
set -e

# Database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Setting up admin user..."
python manage.py shell << END
from django.contrib.auth.models import User
import os

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'✓ Superuser {username} created')
else:
    print(f'✓ Superuser {username} already exists')
END

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run security checks
echo "Running security checks..."
python manage.py check --deploy

# Run SAST scans
echo "Running security audits..."
pip-audit || echo "Warning: Some dependencies may have known vulnerabilities"
bandit -r . -f json -o bandit-report.json || echo "Warning: Code security issues detected"

echo "✓ Deployment ready!"
