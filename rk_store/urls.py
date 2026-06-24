"""
RK Store — Root URL Configuration

URL structure:
    /           → Serve frontend (index.html)
    /api/       → Django REST API (products, orders)
    /admin/     → Django admin panel
    /health/    → Health check endpoint (App Service probes)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.generic import TemplateView


def health_check(request):
    """
    Simple health check endpoint.
    Azure App Service uses this to verify the app is running.
    Returns HTTP 200 with a JSON payload.
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'RK Store API',
        'version': '1.0.0',
    })


urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Health check — used by Azure App Service and load balancer probes
    path('health/', health_check, name='health-check'),

    # REST API — all store endpoints (products, orders) added in Stage 5
    path('api/', include('store.urls')),

    # Frontend — serve index.html at root (SPA catch-all)
    path('', TemplateView.as_view(template_name='index.html'), name='frontend'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
