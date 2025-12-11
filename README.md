# Arklet - A basic ARK resolver

![lint_python](https://github.com/internetarchive/arklet/actions/workflows/lint_python.yml/badge.svg)


## What is an ARK?
See https://arks.org/

## What is Arklet?
Arklet is a Python Django application for minting, binding, and resolving ARKs.
It is intended to follow best practices set out by https://arks.org/.

Technical design notes:
- Django is the only required dependency.
- Supports each Django and Python version that is itself supported by the maintainers.
  - Tests are run against the upcoming versions of Python and Django as well.
- This repo can be run as a standalone service
- ...or the ark package can be installed as a reusable app in other Django projects.
- Arklet is database agnostic.

Arklet is developed with uv, pytest, ruff, tox, and more.

## Running Locally

Use the provided `docker-compose.yml` to spin-up a local Postgres.

```
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

## Running tests

uv run pytest .

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

See arklet/entrypoints/settings.py for the full list of options to put in your config file.