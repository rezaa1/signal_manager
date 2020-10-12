#!/bin/sh
echo "Waiting for postgres..."
while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py flush --no-input
python manage.py migrate auth
python manage.py migrate --run-syncdb
#python manage.py makemigrations auth *

gunicorn signalmanager.wsgi:application --bind 0.0.0.0:$WEB_HTTP_INTERNAL

exec "$@"
