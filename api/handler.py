"""
Vercel serverless handler for Django ASGI application.
This file is invoked by Vercel's runtime and routes all requests to Django.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academic_portfolio.settings')

# Import Django ASGI application
import django
from django.core.wsgi import get_wsgi_application
from django.core.asgi import get_asgi_application

# Initialize Django
django.setup()

# Get ASGI application
asgi_app = get_asgi_application()

# Vercel handler - converts HTTP request to ASGI format
async def handler(request):
    """
    Vercel serverless function handler.
    Converts Vercel HTTP request format to ASGI and returns response.
    """
    return await asgi_app(request)


# Also expose WSGI for compatibility
wsgi_app = get_wsgi_application()


def application(environ, start_response):
    """
    WSGI application for compatibility.
    """
    return wsgi_app(environ, start_response)
