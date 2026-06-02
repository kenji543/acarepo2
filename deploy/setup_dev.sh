#!/bin/bash
# Local development setup script

set -e

echo "🚀 Academic Portfolio Repository - Development Setup"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/Scripts/activate || source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please fill in .env with your configuration"
fi

# Create logs directory
mkdir -p logs

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser --noinput \
  --username=admin \
  --email=admin@localhost || echo "Admin user may already exist"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run security checks
echo "Running Django security checks..."
python manage.py check

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the development server, run:"
echo "  python manage.py runserver"
echo ""
echo "Admin interface: http://localhost:8000/admin"
echo "API documentation: http://localhost:8000/api/"
