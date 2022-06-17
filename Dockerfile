FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1
ENV DOCKERIZE_VERSION v0.6.1
ENV WORK_DIR /usr/src/crm

WORKDIR ${WORK_DIR}

COPY requirements.txt ${WORK_DIR}

RUN apt update \
 && apt install -y \
    binutils \
    gcc \
    libpq-dev \
    libproj-dev \
    gdal-bin \
    wget \
 && pip install uvicorn \
 && pip install -r requirements.txt \
 && wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
 && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
 && apt purge -y wget \
 && apt autoremove -y \
 && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
 && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["uvicorn", "hyakumori_crm.asgi:application", "--host", "0.0.0.0", "--header Server:apache"]
