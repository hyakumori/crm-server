FROM nikolaik/python-nodejs:latest as BUILD_PHASE
ENV PYTHONUNBUFFERED 1

ARG HYAKUMORI_VERSION=${HYAKUMORI_VERSION}

WORKDIR /app

RUN mkdir -p /app/hyakumori_crm/static/hyakumori_crm
COPY ./hyakumori_crm/static/hyakumori_crm/package.json /app/hyakumori_crm/static/hyakumori_crm/package.json
RUN yarn

VOLUME /root/.cache
RUN pip install -U pip setuptools

# COPY ./requirements.txt requirements.txt
# RUN pip install -r requirements.txt

COPY . /app

# run build_assets cmd to generate static output, then run sdist to pack up,
# using LIGHT_BUILD to ignore build_assets in sdist command
RUN python setup.py build_assets --inplace && HYAKUMORI_VERSION=${HYAKUMORI_VERSION} HYAKUMORI_LIGHT_BUILD=1 python setup.py sdist


FROM nikolaik/python-nodejs:latest as SERVE_PHASE
ENV PYTHONUNBUFFERED 1

ARG HYAKUMORI_VERSION=${HYAKUMORI_VERSION}

WORKDIR /app
COPY --from=BUILD_PHASE /app/dist/hyakumori_crm-${HYAKUMORI_VERSION}.tar.gz /tmp/hyakumori_crm-${HYAKUMORI_VERSION}.tar.gz
RUN tar -zxvf /tmp/hyakumori_crm-${HYAKUMORI_VERSION}.tar.gz --strip-components=1 -C /app

VOLUME /root/.cache

RUN pip install uvicorn
RUN HYAKUMORI_LIGHT_BUILD=1 pip install .

EXPOSE 8000

CMD uvicorn hyakumori_crm.asgi:application
