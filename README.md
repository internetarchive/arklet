# Arklet - A basic ARK resolver

![lint_python](https://github.com/internetarchive/arklet/actions/workflows/lint_python.yml/badge.svg)


## What is an ARK?
See https://arks.org/

## What is Arklet?
Arklet is a Python Django application for minting, binding, and resolving ARKs.
It is intended to follow best practices set out by https://arks.org/.

Technical design notes:
- Django is the only required dependency.
- Supports each Django and Python version that is itself supported by the maintainers (Python 3.7-3.10, Django 3.2.x-4.0.x).
    - Tests are run against the upcoming versions of Python and Django as well. 
- This repo can be run as a standalone service 
- ...or the ark package can be installed as a reusable app in other Django projects. 
    - If using the included arklet/settings.py file django-environ is also required.
- Arklet is database agnostic.

Arklet is developed with poetry, pytest, black, tox, and more.

## Running

### Locally with Postgres

Create the default `.env` file in the project's root directory

```
# /!\ Set your own secret key /!\
ARKLET_DJANGO_SECRET_KEY=[YOUR_SECRET]

# For local development, set to True
ARKLET_DEBUG=True
```

The following steps walk through running Postgres, installing with poetry, and starting
the app. You can omit any of the extras listed in the poetry install step if they are
not used in your deployment. The included arklet/settings.py file does require environ.
You can skip installing the development dependencies by passing `--no-dev` to poetry.
Django is the only required dependency.
```
cd path/to/project
mkdir postgres-data
docker run --name arklet-postgres -v postgres-data:/var/lib/postgresql/data \
    -p 5432:5432 \
    -e POSTGRES_USER=arklet -e POSTGRES_PASSWORD=arklet \
    -d postgres
poetry install --extras "postgres sentry environ"
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
poetry run python manage.py runserver
```

### Separate dockers
Using docker, we can use a [this provided](./docker/env.docker.local) config file.

See above for running PostgreSQL, and run the **Arklet** docker as follows (in *bash*):
```
docker build \
    --target dev \
    -t "arklet" -f ./Dockerfile . \
    --build-arg ENV=DEV \
&& docker run --rm -it \
    -p 8000:8000 \
    --env-file=./docker/env.docker.local \
    -e ARKLETDEBUG="true" \
    --name arklet \
    -v `pwd`/ark:/app/ark \
    -v `pwd`/ark_import:/app/ark_import \
    -v `pwd`/arklet:/app/arklet \
    arklet
```

### With docker-compose
Using the provided `docker-compose.yml` with default settings in the [docker
configuration directory](./docker) :

```
docker-compose up
```

By default, the folders `ark`, `ark_import` and `arklet` are mounted in the
container. Should you wish to attach a console to the `arklet` container (needed
to create the django superuser) :
```
# In another shell
docker exec -it arklet_django /bin/bash
# You're now in the docker container
./manage.py createsuperuser
```

### First steps
Create your first NAAN, Key, and Shoulder in the admin:
127.0.0.1:8000/admin

And by the way, you now host a working ARK resolver! You can already
try the following ones :
- [http://127.0.0.1:8000/ark:/13960/t5n960f7n](http://127.0.0.1:8000/ark:/13960/t5n960f7n)
- [http://127.0.0.1:8000/ark:/67375/C0X-SPWFRSGR-N](http://127.0.0.1:8000/ark:/67375/C0X-SPWFRSGR-N)
- [http://127.0.0.1:8000/ark:/12148/bpt6k65358454](http://127.0.0.1:8000/ark:/12148/bpt6k65358454)
- ...

Happy minting, binding, and resolving!

## Configuration Options

See arklet/settings.py for the full list of options to put in your config file.

## Deploying
### With docker
Using the provided Dockerfile (is you wish to set a build target, use `prod`, 
but being the default target you can skip this), provide the following values
in your environment:

- ARKLET_DJANGO_SECRET_KEY=[YOUR_SECRET]
- ARKLET_DEBUG=False
- ARKLET_HOST=0.0.0.0
- ARKLET_PORT=[Port of choice]
- ARKLET_POSTGRES_NAME=[DB NAME]
- ARKLET_POSTGRES_USER=[DB USER]
- ARKLET_POSTGRES_PASSWORD=[DB PASS]
- ARKLET_POSTGRES_HOST=[DB HOST]
- ARKLET_POSTGRES_PORT=[DB PORT]
