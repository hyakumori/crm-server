# Hyakumori crm

[![pipeline status](https://gitlab.com/datafluct/hyakumori_crm/badges/develop/pipeline.svg)](https://gitlab.com/datafluct/hyakumori_crm/-/commits/develop)
[![coverage report](https://gitlab.com/datafluct/hyakumori_crm/badges/develop/coverage.svg)](https://gitlab.com/datafluct/hyakumori_crm/-/commits/develop)

## Requirements

- Python>=3.7 (consider using `pyenv` to manage python version).

- Vuejs

- Postgresql>=11

## Installation

### Postgres

- Start postgres service with docker

```
$ docker run --name postgres \
    --mount type=volume,source=postgres11,destination=/var/lib/postgresql/data \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_DB=hyakumori_local \
    --publish 5432:5432 \
    postgres:11-alpine
```

- Or use `docker-compose` with provided `docker-compose.infra.yml`

### REDIS

```
$ docker run --name redis \
    --mount type=volume,source=redis,destination=/data \
    --publish 6379:6379 \
    redis:alpine
```

- Or use `docker-compose` with provided `docker-compose.infra.yml`

### Python

- Create virtualenv: `python -m venv venv`

- Activate virtualenv: `source venv/bin/activate`

- Update `pip` and `setuptools`: `pip install -U pip setuptools`

- Install `pip-tools`: `pip install pip-tools`

### Run on local

1. Install once with `HYAKUMORI_LIGHT_BUILD=1 pip install -e .[dev]`
2. Copy `.env.example` to `.env` and fill necessary variables for both backend and fontend.
3. Run dev server with `STATIC_DIR="" hyakumori runserver`. You might want to set `STATIC_DIR=""` in `.env`.
4. [FRONTEND] Move to `hyakumori_crm/static/hyakumori_crm` run `yarn`. Skip if at step 3, STATIC_DIR is set.

### Dependency management

#### Front-end

Using `yarn`.

#### Backend

Using `pip-tools`

**Runtime**

- Add a dependeny to requirements.in, consider pin its version.

- Compile to `requirements.txt`: `pip-compile --generate-hashes setup.py`

**Dev**

- Add a dependeny to requirements-dev.in, consider pin its version.

- Compile to `requirements-dev.txt`: `pip-compile requirements-dev.in`

Remember to reinstall package.

### Using Docker build

- `Dockerfile.full` is for building all in one image, included compiling Front-end
- `Dockerfile` is used mainly for CI to build serve-able image using previous job artifacts
- See `docker-compose.infra.yml` for local infrastructure reference
- Assume `.env`

```
DEBUG=True
SECRET_KEY=0fdafa9ea1f1436cb1d3ff56fcd95586
DATABASE_URL=postgres://postgres:postgres@localhost:5432/hyakumori_crm_local
STATIC_DIR=hyakumori_crm/static/hyakumori_crm/dist
```

IMPORTANT: Set `STATIC_DIR` correctly as above.

- Examples docker build

```
docker build -f Dockerfile.full --build-arg HYAKUMORI_VERSION=0.1.0 -t hyakumori_crm:0.1.0 .
docker run --rm -it --env-file .env --network=host --name=hyakumori_crm_test hyakumori_crm:latest
```

### Mailhog

```
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

### Task queue
- Using `django-q` for async task and schedule
- Run `./manage.py setup_schedule_tasks` to set up schedule tasks
- Run `./manage.py qcluster` to start workers
- Check info by running `./manage.py qinfo`
