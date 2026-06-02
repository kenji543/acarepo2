"""
Django settings for academic_portfolio project.
"""

import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url
import environ

from .cloudinary_settings import (
    build_django_cloudinary_storage,
    configure_cloudinary,
    is_cloudinary_configured,
)

# Initialize environment variables (non-Cloudinary settings)
env = environ.Env(
    DEBUG=(bool, False),
    SECURE_SSL_REDIRECT=(bool, True),
)

# Load local .env for development; never override variables already set by the host
_env_file = Path(__file__).resolve().parent.parent / ".env"
if _env_file.exists():
    environ.Env.read_env(_env_file, overwrite=False)

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=False)

# ===== ALLOWED HOSTS (Railway + local development) =====
def _hosts_from_env(*var_names: str) -> list[str]:
    """Parse comma-separated host lists from environment variables."""
    hosts: list[str] = []
    for name in var_names:
        raw = os.environ.get(name, "")
        if raw:
            hosts.extend(h.strip() for h in raw.split(",") if h.strip())
    return hosts


_DEFAULT_ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "acarepo2-production.up.railway.app",
    ".up.railway.app",  # Railway *.up.railway.app services
    ".railway.app",  # Railway-generated subdomains
]

ALLOWED_HOSTS = list(_DEFAULT_ALLOWED_HOSTS)
ALLOWED_HOSTS.extend(_hosts_from_env("DJANGO_ALLOWED_HOSTS", "ALLOWED_HOSTS"))

# Railway injects the public service hostname at runtime
_railway_public = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "").strip()
if _railway_public:
    if "://" in _railway_public:
        _railway_public = urlparse(_railway_public).hostname or _railway_public
    ALLOWED_HOSTS.append(_railway_public)

# Deduplicate while preserving order
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))

# HTTPS form posts (login, logout, uploads) from production domains
CSRF_TRUSTED_ORIGINS = []
for _host in ALLOWED_HOSTS:
    if _host.startswith("."):
        continue
    if _host in ("localhost", "127.0.0.1"):
        CSRF_TRUSTED_ORIGINS.extend(
            (f"http://{_host}", f"https://{_host}")
        )
    else:
        CSRF_TRUSTED_ORIGINS.append(f"https://{_host}")
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS))

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'cloudinary_storage',
    'cloudinary',
    'django_filters',
    'axes',
    'django_ratelimit',
    
    # Local apps
    'portfolio',
    'api',
    'auth_service',
    'security',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',  # Must be after AuthenticationMiddleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'academic_portfolio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'portfolio' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'academic_portfolio.wsgi.application'

# ===== DATABASE CONFIGURATION =====
# Railway automatically injects DATABASE_URL
# dj_database_url parses it and creates the connection dict
if os.environ.get('DATABASE_URL'):
    # Production: Use environment DATABASE_URL (Railway, Supabase, etc)
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    # Enable atomic transactions for production database
    DATABASES['default']['ATOMIC_REQUESTS'] = True
else:
    # Development: Fallback to SQLite locally
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'ATOMIC_REQUESTS': True,
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session authentication (template frontend)
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/login/'

# ===== CLOUDINARY CONFIGURATION =====
# Credentials are read only from the process environment (see cloudinary_settings.py).
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "").strip()
CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "").strip()
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "").strip()
CLOUDINARY_CONFIGURED = is_cloudinary_configured()

if CLOUDINARY_CONFIGURED:
    configure_cloudinary()
    CLOUDINARY_STORAGE = build_django_cloudinary_storage()
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
else:
    CLOUDINARY_STORAGE = {}
    # Allow collectstatic / migrations without Cloudinary; uploads require host env vars.
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# ===== DJANGO REST FRAMEWORK CONFIGURATION =====
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}

# ===== JWT CONFIGURATION =====
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# ===== AUTHENTICATION BACKENDS =====
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # django-axes 5.0+ authentication
    'django.contrib.auth.backends.ModelBackend',  # Default Django auth backend
]

# ===== CORS CONFIGURATION =====
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS', default='http://localhost:3000,http://127.0.0.1:3000').split(',')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ===== SYSTEM CHECKS CONFIGURATION =====
# Silence django_ratelimit cache warning - using default LocMemCache for now
# Production: Use Redis or DatabaseCache for distributed deployments
SILENCED_SYSTEM_CHECKS = ['django_ratelimit.E003']

# ===== DJANGO-AXES CONFIGURATION (Brute-force protection) =====
AXES_FAILURE_LIMIT = 5  # Lock after 5 failed attempts
AXES_COOLOFF_DURATION = timedelta(minutes=15)  # Lock duration
AXES_LOCK_OUT_AT_FAILURE = True
# AXES_USE_USER_AGENT = True  # DEPRECATED in django-axes 5.0+ - REMOVED
AXES_LOCKOUT_TEMPLATE = 'security/lockout.html'
AXES_VERBOSE = True

# ===== SECURITY SETTINGS =====
SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT', default=not DEBUG)
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'"),
    "img-src": ("'self'", "data:", "https://res.cloudinary.com"),
    "style-src": ("'self'", "'unsafe-inline'"),
}
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ===== LOGGING CONFIGURATION =====
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'academic_portfolio.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'axes': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
SILENCED_SYSTEM_CHECKS = ['django_ratelimit.W001']
SILENCED_SYSTEM_CHECKS = ['django_ratelimit.E003']
