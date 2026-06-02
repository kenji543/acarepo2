"""
WSGI config for academic_portfolio project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academic_portfolio.settings')

application = get_wsgi_application()
