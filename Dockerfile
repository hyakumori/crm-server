FROM nikolaik/python-nodejs:latest as BUILD_PHASE
ENV PYTHONUNBUFFERED 1

ARG MAMORI_VERSION=${MAMORI_VERSION}

WORKDIR /app

RUN mkdir -p /app/mamori/static/mamori
COPY ./mamori/static/mamori/package.json /app/mamori/static/mamori/package.json
RUN yarn

VOLUME /root/.cache
RUN pip install -U pip setuptools

# COPY ./requirements.txt requirements.txt
# RUN pip install -r requirements.txt

COPY . /app

# run build_assets cmd to generate static output, then run sdist to pack up,
# using LIGHT_BUILD to ignore build_assets in sdist command
RUN python setup.py build_assets --inplace && MAMORI_VERSION=${MAMORI_VERSION} MAMORI_LIGHT_BUILD=1 python setup.py sdist


FROM nikolaik/python-nodejs:latest as SERVE_PHASE
ENV PYTHONUNBUFFERED 1

ARG MAMORI_VERSION=${MAMORI_VERSION}

WORKDIR /app
COPY --from=BUILD_PHASE /app/dist/mamori-${MAMORI_VERSION}.tar.gz /tmp/mamori-${MAMORI_VERSION}.tar.gz
RUN tar -zxvf /tmp/mamori-${MAMORI_VERSION}.tar.gz --strip-components=1 -C /app

VOLUME /root/.cache

RUN pip install uvicorn
RUN MAMORI_LIGHT_BUILD=1 pip install .

EXPOSE 8000

CMD uvicorn mamori.asgi:application
