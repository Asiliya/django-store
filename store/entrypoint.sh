#!/bin/bash
echo "Running from entrypoint.sh"

# Run all migrations
python manage.py migrate

# Collect static files
#python3 src/manage.py collectstatic --noinput

# Create superuser
python manage.py create_superuser

# Start the server
python manage.py runserver 0.0.0.0:8000