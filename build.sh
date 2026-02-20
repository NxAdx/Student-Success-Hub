#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Build Tailwind CSS
echo "Building Tailwind..."
cd theme/static_src
npm install
npm run build
cd ../..

# Verify Tailwind build output
echo "Checking for compiled CSS..."
if [ -f "theme/static/css/dist/styles.css" ]; then
    echo "Tailwind CSS built successfully."
else
    echo "ERROR: Tailwind CSS file not found at theme/static/css/dist/styles.css"
    ls -R theme/static
fi

# Collect static files
echo "Collecting static files..."
rm -rf staticfiles
mkdir -p staticfiles
python manage.py collectstatic --no-input --clear

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if needed
echo 'Checking/Creating superuser...'
python create_superuser.py

# Final production check
echo 'Running final production check...'
python manage.py check --deploy

echo 'Build complete!'
