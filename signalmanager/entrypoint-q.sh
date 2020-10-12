#!/bin/sh
echo "Waiting for postgres..."
while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py process_tasks --queue trade-queue --duration 0 --sleep 2

exec "$@"
