"""
Django settings for the arklet project.
"""

from pathlib import Path
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def get_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("ARKLET_DJANGO_SECRET_KEY", "test")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool("ARKLET_DEBUG", False)

ARKLET_HOST = os.environ.get("ARKLET_HOST", "127.0.0.1")

ALLOWED_HOSTS = [
    ARKLET_HOST,
    "wbgrp-svc302.us.archive.org",
    "qa-ark.archive.org",
    "ark.archive.org",
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "arklet.ark.apps.ArkConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "arklet.entrypoints.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "arklet.entrypoints.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        # "ENGINE": "django.db.backends.sqlite3",
        # "NAME": BASE_DIR / "db.sqlite3",
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("ARKLET_POSTGRES_NAME", "arklet"),
        "HOST": os.environ.get("ARKLET_POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("ARKLET_POSTGRES_PORT", "5432"),
        "USER": os.environ.get("ARKLET_POSTGRES_USER", "arklet"),
        "PASSWORD": os.environ.get("ARKLET_POSTGRES_PASSWORD", "arklet"),
        "DISABLE_SERVER_SIDE_CURSORS": True,  # required for pgbouncer transaction mode
    }
}


AUTH_USER_MODEL = "ark.User"


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = os.environ.get("ARKLET_STATIC_ROOT", "static")

MEDIA_ROOT = os.environ.get("ARKLET_MEDIA_ROOT", "media")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SENTRY_DSN = os.environ.get("ARKLET_SENTRY_DSN", "")
SENTRY_SAMPLE_RATE = 1 / get_int("ARKLET_SENTRY_TRANSACTIONS_PER_TRACE", 1)
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=SENTRY_SAMPLE_RATE,
        send_default_pii=True,
    )

# Django is moving from assuming the protocol of URLField is https.
# This setting should be removed in Django 6.
FORMS_URLFIELD_ASSUME_HTTPS = True
