FROM python:3.7
ENV PYTHONUNBUFFERED 1

ARG HYAKUMORI_VERSION=${HYAKUMORI_VERSION}

RUN pip install -U pip setuptools wheel
RUN pip install uvicorn

COPY ./dist/hyakumori_crm-${HYAKUMORI_VERSION}.tar.gz /tmp/hyakumori_crm-${HYAKUMORI_VERSION}.tar.gz

RUN pip install /tmp/hyakumori_crm-${HYAKUMORI_VERSION}.tar.gz

EXPOSE 8000

CMD uvicorn hyakumori_crm.asgi:application --host 0.0.0.0 --port 8000 --header Server:apache
