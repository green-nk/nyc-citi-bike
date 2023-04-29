FROM apache/airflow:2.5.3-python3.9

USER root
RUN apt-get update && \
    apt-get install -yqq wget unzip vim git
USER airflow

ADD requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
