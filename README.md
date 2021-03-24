# Hyakumori CRM API

A geospatial-enabled Python API for the Hyakumori CRM.

## Requirements

- python >= 3.7
- GEOS >= 3.5
- GDAL >= 2.0
- PROJ.4 >= 4.0
- PostgreSQL >= 9.5+
- PostGIS >= 2.2

The application also expects the following services to be running in tandem with django:

* redis
* geoserver (with the [S3 Geotiff plugin](https://docs.geoserver.org/latest/en/user/community/s3-geotiff/index.html))
* mailhog

Each of these can be run locally or from a suitable docker container. 

## Installation

1. Copy `.env.example` to `.env` and fill necessary variables:

```
cp .env.example .env
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

## How to use

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

## Contributing and Support

The Hyakumori Project appreciates any [contributions](https://github.com/hyakumori/.github/blob/main/CONTRIBUTING.md).

## Authors

The Hyakumori CRM API was developed by the Hyakumori Team with additional contributions from:

- [Iosefa Percival](https://github.com/iosefa)
- [Nathaniel Nasarow](https://github.com/Torgian)
- ... [and others](https://github.com/hyakumori/crm-server/graphs/contributors)

## LICENSE

This program is free software. See [LICENSE](LICENSE) for more information.
