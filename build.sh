#!/bin/bash
# Vercel Build Script
# This runs during Vercel build phase

set -e

echo "🔧 Installing dependencies..."
pip install -r requirements.txt

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🗄️  Running migrations..."
python manage.py migrate --noinput || true

echo "✅ Build complete!"
