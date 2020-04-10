FROM nikolaik/python-nodejs:python3.7-nodejs12
ENV PYTHONUNBUFFERED 1

ARG HYAKUMORI_VERSION=${HYAKUMORI_VERSION}

WORKDIR /app
RUN pip install uvicorn

COPY ./requirements.txt /app
RUN pip install -r requirements.txt

COPY ./dist/hyakumori_crm-${HYAKUMORI_VERSION}.tar.gz /tmp/hyakumori_crm-${HYAKUMORI_VERSION}.tar.gz
RUN tar -zxvf /tmp/hyakumori_crm-${HYAKUMORI_VERSION}.tar.gz --strip-components=1 -C /app

RUN HYAKUMORI_LIGHT_BUILD=1 pip install .

EXPOSE 8000

CMD hyakumori inject_envs && uvicorn hyakumori_crm.asgi:application --host 0.0.0.0 --port 8000
