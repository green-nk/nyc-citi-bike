FROM python:3.9.7-slim-buster

RUN apt-get update && \
    apt-get install -yqq git

RUN mkdir -p /root/.dbt
WORKDIR /usr/app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir dbt-core dbt-bigquery

CMD sleep infinity