FROM apache/airflow:2.5.3-python3.9

# Switch user to root when using apt
USER root

# Install necessary utility command-line tools
RUN apt-get update && \
    apt-get install -yqq wget unzip vim

# Swithc back to airflow user
USER airflow
