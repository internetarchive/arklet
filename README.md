# Arklet - A basic ARK resolver

## What is an ARK?
See https://arks.org/

## What is Arklet?
Arklet is a Python Django application for minting, binding, and resolving ARKs. It is intended to follow best practices set out by https://arks.org/.

## Running Locally with Postgres

Create the default config YAML file: **/etc/arklet.yml** 

- Set a value for **ARKLET_DJANGO_SECRET_KEY**.
- For local development, set **ARKLET_DEBUG** to True. 

Run Postgres, install into virtual environment, and start the app:
```
cd path/to/project
mkdir postgres-data
docker run --name arklet-postgres -v postgres-data:/var/lib/postgresql/data \
    -p 5432:5432 \
    -e POSTGRES_USER=arklet -e POSTGRES_PASSWORD=arklet \
    -d postgres:10
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Create your first NAAN, Key, and Shoulder in the admin:
127.0.0.1:8000/admin

Happy minting, binding, and resolving!

## Configuration Options

See arklet/settings.py for the full list of options to put in your config file.