#!/bin/bash
echo "Running from entrypoint.sh"

# Run all migrations
python manage.py migrate

python manage.py loaddata products/fixtures/categories.json
python manage.py loaddata products/fixtures/products.json

# Collect static files
#python3 src/manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Start the server
python manage.py runserver 0.0.0.0:8000