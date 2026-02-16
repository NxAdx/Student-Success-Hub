#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Build Tailwind CSS
# We need to install npm dependencies first
echo "Building Tailwind..."
cd theme/static_src
npm install
npm run build
cd ../..

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate
