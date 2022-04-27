#!/usr/bin/env bash
# Getting static files for Admin panel hosting!
set -e

# White while DB is spinning up
echo "pg_isready -h $ARKLET_POSTGRES_HOST -p $ARKLET_POSTGRES_PORT"
while ! pg_isready -h $ARKLET_POSTGRES_HOST -p $ARKLET_POSTGRES_PORT; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
done

# Following rules depend on what you expect from django dev docker
# ./manage.py collectstatic --noinput
# ./manage.py compress --force

./manage.py migrate
./manage.py createsuperuser

./manage.py runserver 0.0.0.0:$ARKLET_PORT
# gunicorn config.wsgi:application -w 2 -b :8880 --reload
