"""
RK Store — Django Settings
Multi-Tier E-Commerce Web Application on Azure
George Brown College — Cloud Computing Capstone

Architecture:
    Frontend  : HTML5 / Bootstrap 5 (Azure App Service)
    Backend   : Django REST API     (Azure App Service + Auto-Scale)
    Database  : Azure SQL Database
    Secrets   : Azure Key Vault     (accessed via Managed Identity)
    Telemetry : Application Insights
"""

import os
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
# KEY VAULT — Secret Loader
# ════════════════════════════════════════════════════════════════════════════
# On Azure App Service → uses System-Assigned Managed Identity automatically.
# Locally               → uses your `az login` credentials (Azure CLI).
# No passwords ever stored in source code.

def get_secret(secret_name: str, fallback: str = '') -> str:
    """
    Load a secret from Azure Key Vault.

    Production (App Service):
        Managed Identity authenticates to Key Vault with zero credentials.

    Local development:
        DefaultAzureCredential falls back to Azure CLI (`az login`).
        You can also set the env var directly (e.g. in .env) as a fallback.

    Secret naming convention (Key Vault):
        django-secret-key           → Django SECRET_KEY
        db-server                   → Azure SQL server FQDN
        db-name                     → Database name
        db-username                 → SQL admin username
        db-password                 → SQL admin password
        appinsights-connection-str  → Application Insights connection string
        acs-email-connection-str    → Azure Communication Services Email
        acs-sms-connection-str      → Azure Communication Services SMS
        acs-sender-email            → Verified sender email address
        acs-sender-phone            → Verified sender phone number
    """
    kv_uri = os.environ.get('KEY_VAULT_URI')

    if kv_uri:
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=kv_uri, credential=credential)
            value = client.get_secret(secret_name).value
            logger.info(f"[KeyVault] ✅ Loaded secret: {secret_name}")
            return value
        except Exception as exc:
            logger.warning(f"[KeyVault] ⚠️  Could not load '{secret_name}': {exc}")

    # Local dev fallback — read matching environment variable
    env_key = secret_name.upper().replace('-', '_')
    value = os.environ.get(env_key, fallback)
    if value:
        logger.debug(f"[KeyVault] Using env fallback for: {secret_name}")
    return value


# ════════════════════════════════════════════════════════════════════════════
# CORE SETTINGS
# ════════════════════════════════════════════════════════════════════════════

SECRET_KEY = get_secret('django-secret-key', fallback='dev-only-key-replace-before-deploy')

# DEBUG must be False in production — controlled via App Service env var
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Add your Azure App Service hostname here (e.g. rk-store.azurewebsites.net)
_allowed = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]


# ════════════════════════════════════════════════════════════════════════════
# INSTALLED APPS
# ════════════════════════════════════════════════════════════════════════════

INSTALLED_APPS = [
    # Django built-ins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',       # Django REST Framework — API layer
    'corsheaders',          # CORS headers for frontend requests

    # RK Store application
    'store',
]


# ════════════════════════════════════════════════════════════════════════════
# MIDDLEWARE
# ════════════════════════════════════════════════════════════════════════════

MIDDLEWARE = [
    # CORS must be first so headers are added before any response is sent
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise serves compressed static files without a CDN
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rk_store.urls'


# ════════════════════════════════════════════════════════════════════════════
# TEMPLATES
# ════════════════════════════════════════════════════════════════════════════

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'rk_store.wsgi.application'


# ════════════════════════════════════════════════════════════════════════════
# DATABASE — Azure SQL (via Key Vault)
# ════════════════════════════════════════════════════════════════════════════
# Requires: ODBC Driver 18 for SQL Server installed on the App Service
# Install on App Service via startup script or custom Docker image.

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME':     get_secret('db-name'),
        'USER':     get_secret('db-username'),
        'PASSWORD': get_secret('db-password'),
        'HOST':     get_secret('db-server'),   # e.g. rk-store-sql.database.windows.net
        'PORT':     '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': (
                'Encrypt=yes;'
                'TrustServerCertificate=no;'
                'Connection Timeout=30;'
            ),
        },
    }
}


# ════════════════════════════════════════════════════════════════════════════
# PASSWORD VALIDATION
# ════════════════════════════════════════════════════════════════════════════

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ════════════════════════════════════════════════════════════════════════════
# LOCALISATION
# ════════════════════════════════════════════════════════════════════════════

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'America/Toronto'
USE_I18N      = True
USE_TZ        = True


# ════════════════════════════════════════════════════════════════════════════
# STATIC FILES — WhiteNoise (serves frontend from App Service)
# ════════════════════════════════════════════════════════════════════════════

STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# CompressedManifestStaticFilesStorage adds cache-busting hashes
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ════════════════════════════════════════════════════════════════════════════
# CORS — Allow frontend to call API
# ════════════════════════════════════════════════════════════════════════════
# Add your App Service URL to CORS_ALLOWED_ORIGINS env var in production
# e.g. https://rk-store.azurewebsites.net

_cors_origins = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000'
)
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(',') if o.strip()]
CORS_ALLOW_CREDENTIALS = True


# ════════════════════════════════════════════════════════════════════════════
# DJANGO REST FRAMEWORK
# ════════════════════════════════════════════════════════════════════════════

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}


# ════════════════════════════════════════════════════════════════════════════
# AZURE COMMUNICATION SERVICES — Notifications (Stage 6)
# ════════════════════════════════════════════════════════════════════════════

ACS_EMAIL_CONNECTION_STRING = get_secret('acs-email-connection-str')
ACS_SMS_CONNECTION_STRING   = get_secret('acs-sms-connection-str')
ACS_SENDER_EMAIL            = get_secret('acs-sender-email')
ACS_SENDER_PHONE            = get_secret('acs-sender-phone')


# ════════════════════════════════════════════════════════════════════════════
# APPLICATION INSIGHTS — Telemetry (Stage 9)
# ════════════════════════════════════════════════════════════════════════════

APPINSIGHTS_CONNECTION_STRING = get_secret('appinsights-connection-str')

# Wire Django logging to Application Insights when connection string is set
if APPINSIGHTS_CONNECTION_STRING:
    from opencensus.ext.azure.log_exporter import AzureLogHandler
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'azure': {
                'class': 'opencensus.ext.azure.log_exporter.AzureLogHandler',
                'connection_string': APPINSIGHTS_CONNECTION_STRING,
            },
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['azure', 'console'],
            'level': 'INFO',
        },
    }
else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {'class': 'logging.StreamHandler'},
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }


# ════════════════════════════════════════════════════════════════════════════
# SECURITY HEADERS (enforced in production, skipped in DEBUG)
# ════════════════════════════════════════════════════════════════════════════

if not DEBUG:
    SECURE_SSL_REDIRECT              = True
    SECURE_HSTS_SECONDS              = 31536000   # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS   = True
    SECURE_HSTS_PRELOAD              = True
    SECURE_BROWSER_XSS_FILTER        = True
    SECURE_CONTENT_TYPE_NOSNIFF      = True
    SESSION_COOKIE_SECURE            = True
    CSRF_COOKIE_SECURE               = True
    X_FRAME_OPTIONS                  = 'DENY'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
