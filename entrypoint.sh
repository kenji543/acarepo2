#!/bin/bash
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Creating superuser if needed..."
python manage.py shell << END
from django.contrib.auth.models import User
import os

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superuser {username} created successfully')
else:
    print(f'Superuser {username} already exists')
END

echo "Starting gunicorn..."
exec gunicorn academic_portfolio.wsgi:application --bind 0.0.0.0:8000
