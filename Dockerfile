# Multi-stage unique docker build script, provides both dev & prod environments

# ----------------------------------------------------
# Base-image
# ----------------------------------------------------
FROM python:3.9-slim-buster as common-base
# Django directions: https://blog.ploetzli.ch/2020/efficient-multi-stage-build-django-docker/
# Pip on docker : https://pythonspeed.com/articles/multi-stage-docker-python/
# https://blog.mikesir87.io/2018/07/leveraging-multi-stage-builds-single-dockerfile-dev-prod/
# https://pythonspeed.com/articles/base-image-python-docker-images/

# Default environment: Dev
ARG ENV=dev

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

ENV HOST=0.0.0.0 \
    PORT=8000

WORKDIR /app

COPY ./docker/install-packages.sh .
RUN ./install-packages.sh

# ----------------------------------------------------
# Install dependencies
# ----------------------------------------------------
FROM common-base AS dependencies
ENV PATH="/opt/venv/bin:$PATH"

#     apt-get install build-essential -y
COPY requirements.txt /app/

RUN pip install --target /opt/packages -r requirements.txt

# ----------------------------------------------------
# Copy project
# ----------------------------------------------------
FROM common-base AS app-run
COPY --from=dependencies /opt/packages /opt/packages
ENV PYTHONPATH "${PYTHONPATH}:/opt/packages"
# ENV  PYTHONPATH="$PYTHONPATH:/app/lemarche:/app/config"
COPY ./ark ./ark
COPY ./ark_import ./ark_import
COPY ./arklet ./arklet
COPY ./manage.py ./manage.py
COPY ./docker/entrypoint.sh ./entrypoint.sh

# ----------------------------------------------------
# Run Dev
# ----------------------------------------------------
FROM app-run AS dev
ENV ENV="dev" \
    ARKLET_DEBUG="True"

CMD ["bash"]

# ----------------------------------------------------
# Run Prod
# ----------------------------------------------------
FROM app-run AS prod
ENV ENV="prod" \
    ARKLET_DEBUG="False"

CMD ["./entrypoint.sh"]

# # For some _real_ performance, at cost of ease of use:
# FROM python:3.9-alpine as prod
# ENV PATH="/opt/venv/bin:$PATH"
# COPY . .
# RUN apk add python3-dev build-base linux-headers pcre-dev
# RUN pip install uwsgi
