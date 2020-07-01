#!/bin/sh
echo "Waiting for postgres..."
while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# python manage.py flush --no-input
python manage.py makemigrations task
python manage.py makemigrations
python manage.py migrate

gunicorn signalmanager.wsgi:application --bind 0.0.0.0:8000

exec "$@"
