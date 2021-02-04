# Hyakumori crm

This repository holds the source code for the hyakumori CRM. It contains the source code for both the backend (written 
in Python using the Django framework) and the frontend (written in javascript using the Vue framework). It also
contains data import functions for adding dummy data for development.

## Requirements

- python == 3.7
- 
- GEOS
- GDAL
- PostgreSQL
- PostGIS


## Installation

1. Copy `.env.example` to `.env` and fill necessary variables for both backend and frontend:

```
cp .env.example .env
```

For example:

```
DEBUG=True
SECRET_KEY=0fdafa9ea1f1436cb1d3ff56fcd95586
DATABASE_URL=postgis://postgres:postgres@postgres:5432/hyakumori_crm
STATIC_DIR=hyakumori_crm/static/hyakumori_crm/dist
REDIS_CACHE_URL=redis://redis

ALLOW_HOSTS=*.nip.io,localhost
CORS_ORIGIN_WHITELIST=http://localhost:8080
FRONTEND_URL=http://localhost:8000
TIME_ZONE_PRIMARY=Asia/Tokyo

GEOSERVER_USER=**************
GEOSERVER_PASS=**************
GEOSERVER_URL=http://geoserver:8080/geoserver/
```
