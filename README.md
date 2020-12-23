# Hyakumori crm

This repository holds the source code for the hyakumori CRM. It contains the source code for both the backend (written 
in Python using the Django framework) and the frontend (written in javascript using the Vue framework). It also
contains data import functions for adding dummy data for development.

## Requirements

- docker-compose
- python == 3.7
- yarn >= 1.22.10

## Installation

1. Copy `.env.example` to `.env` and fill necessary variables for both backend and frontend:

```
cp .env.example .env
```

For example:

```
# -------------- BACKEND --------------
DEBUG=True
SECRET_KEY=0fdafa9ea1f1436cb1d3ff56fcd95586
DATABASE_URL=postgis://postgres:postgres@postgres:5432/hyakumori
STATIC_DIR=hyakumori_crm/static/hyakumori_crm/dist
REDIS_CACHE_URL=redis://redis

ALLOW_HOSTS=*.nip.io,localhost
CORS_ORIGIN_WHITELIST=http://localhost:8080
FRONTEND_URL=http://localhost:8000
TIME_ZONE_PRIMARY=Asia/Tokyo

# -------------- FRONTEND --------------
VUE_APP_GRAPHQL_HTTP=http://localhost:8000/graphql
VUE_APP_REST_HTTP=http://localhost:8000/api/v1
```

Note, `EMAIL` settings are removed until proper configuration settings are understood. 

2. Copy `.env.example` to `hyakumori_crm/static/hyakumori_crm/.env` and fill necessary variables for both backend and frontend:

```
cp .env.example hyakumori_crm/static/hyakumori_crm/.env
```

The contents can be the same as the above `.env` file.

3. Run docker-compose to launch services:

```
docker-compose up --b -d
```

## Mailhog

```
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

## Task queue
- Using `django-q` for async task and schedule
- Run `./manage.py setup_schedule_tasks` to set up schedule tasks
- Run `./manage.py qcluster` to start workers
- Check info by running `./manage.py qinfo`
