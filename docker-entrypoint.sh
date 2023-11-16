#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start server
# echo "Starting server"
# python manage.py runserver 0.0.0.0:8000

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn"
exec gunicorn storefront.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 4 \
    --worker-class=gthread \
    --log-level=info