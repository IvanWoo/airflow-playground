ARG PYTHON_VERSION=3.10.4
FROM python:$PYTHON_VERSION-slim

ARG AIRFLOW_USER_HOME=/var/lib/airflow
ARG AIRFLOW_USER="airflow"
ARG AIRFLOW_UID="1000"
ARG AIRFLOW_GID="100"
ENV AIRFLOW_HOME=$AIRFLOW_USER_HOME
# https://stackoverflow.com/a/64102988
ENV AIRFLOW_CONFIG=$AIRFLOW_HOME/airflow.cfg

COPY ./requirements.txt .

RUN mkdir $AIRFLOW_USER_HOME && \
    useradd -ms /bin/bash -u $AIRFLOW_UID airflow && \
    chown $AIRFLOW_USER:$AIRFLOW_GID $AIRFLOW_USER_HOME && \
    buildDeps='freetds-dev libkrb5-dev libsasl2-dev libssl-dev libffi-dev libpq-dev' \
    apt-get update && \
    apt-get install -yqq --no-install-recommends $buildDeps build-essential default-libmysqlclient-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge --auto-remove -yqq $buildDeps && \
    apt-get autoremove -yqq --purge && \
    rm -rf /var/lib/apt/lists/*

USER $AIRFLOW_USER

WORKDIR $AIRFLOW_USER_HOME