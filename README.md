# Arklet - A basic ARK resolver

## What is an ARK?
See https://arks.org/

## What is Arklet?
Arklet is a Python Django application for minting, updating, and resolving ARKs. It is intended to follow best practices set out by https://arks.org/.

## Running Postgres Locally

```
cd path/to/project
mkdir postgres-data
docker run --name arklet-postgres -v postgres-data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres -d postgres:10
```
