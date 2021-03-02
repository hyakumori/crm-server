# Hyakumori crm

This repository holds the source code for the API of the hyakumori CRM. It is written in Python and uses the GeoDjango framework.

## Requirements

- python >= 3.7
- GEOS >= 3.5
- GDAL >= 2.0
- PROJ.4 >= 4.0
- PostgreSQL >= 9.5+
- PostGIS >= 2.2

The application also expects the following services to be running in tandem with django:

* redis
* geoserver
* mailhog

Each of these can be run locally or from a suitable docker container. 

## Installation

1. Copy `.env.example` to `.env` and fill necessary variables:

```
cp .env.example .env
```

For example:

```
DEBUG=True
SECRET_KEY=0fdafa9ea1f1436cb1d3ff56fcd95586
DATABASE_URL=postgis://postgres:postgres@localhost:5432/hyakumori_crm
STATIC_DIR=
REDIS_CACHE_URL=

FRONTEND_DOMAIN=localhost:8080

ALLOWED_HOSTS=.*demo.georeport.org,*.nip.io,localhost,127.0.0.1
CORS_ORIGIN_WHITELIST=http://localhost:8080,http://localhost:5000
TIME_ZONE_PRIMARY=Asia/Tokyo

GEOSERVER_USER=**************
GEOSERVER_PASS=**************
GEOSERVER_URL=http://localhost:8600/geoserver/

EMAIL_HOST=localhost
EMAIL_PORT=1025
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=no
```

2. Install requirements:

Create and active a virtual environment then install requirements: 

```bash
pip install -r requirements.txt
```

2. Create database and load postgis extension:

```bash
createdb -U postgres hyakumori_crm
psql -U postgres hyakumori_crm -c "create extension postgis"
```
 
3. Perform migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create a superuser with a password and grant permissions:
  
```bash
python manage.py createsuperuser
python manage.py crm_setup
```

## Usage

*Important: make sure that geoserver, redis, and mailhog are all running and are accessible at the appropriate ports!*

Launch the GeoDjango application with:

```bash
python manage.py runserver
```

### Managing migrations

To run make and run migrations in the containers:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Task queue
Using `django-q` for async task and schedule:
- Run `./manage.py setup_schedule_tasks` to set up schedule tasks
- Run `./manage.py qcluster` to start workers
- Check info by running `./manage.py qinfo`
