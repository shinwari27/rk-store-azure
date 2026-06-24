#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# RK Store — Azure App Service Startup Script
#
# Set this as the startup command in:
#   Azure Portal → App Service → Configuration → General Settings
#   → Startup Command: bash startup.sh
# ─────────────────────────────────────────────────────────────────────────────

echo "🚀 RK Store — Starting up..."

# Install ODBC Driver 18 for SQL Server (required by mssql-django)
# This runs on every cold start. For production, bake it into a custom
# Docker image instead to reduce startup time.
if ! command -v odbcinst &> /dev/null; then
    echo "📦 Installing ODBC Driver 18..."
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
    curl -sSL https://packages.microsoft.com/config/debian/11/prod.list \
        > /etc/apt/sources.list.d/mssql-release.list
    apt-get update -q
    ACCEPT_EULA=Y apt-get install -y -q msodbcsql18
    echo "✅ ODBC Driver 18 installed."
else
    echo "✅ ODBC Driver 18 already present."
fi

# Collect static files (frontend HTML, CSS, JS → staticfiles/)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Apply any pending database migrations
echo "🗄️  Running migrations..."
python manage.py migrate --noinput

# Start Gunicorn WSGI server
# workers = (2 × CPU cores) + 1 — App Service B1 has 1 vCPU → 3 workers
echo "⚡ Starting Gunicorn..."
gunicorn rk_store.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile '-' \
    --error-logfile '-' \
    --log-level info
