"""
WSGI config for RK Store.

Azure App Service runs this file via Gunicorn:
    gunicorn rk_store.wsgi:application --bind 0.0.0.0:8000

Startup command set in App Service → Configuration → General Settings.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rk_store.settings')

application = get_wsgi_application()
