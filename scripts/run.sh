#!/bin/sh
# This file is autogenerated - DO NOT EDIT!
set -euo pipefail
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${BASE_DIR}/.."
(
cd ${REPO_DIR}

kubectl run airflow-initdb \
    --restart=Never -ti --rm --image-pull-policy=Never \
    --image=my/airflow \
    --env AIRFLOW__CORE__LOAD_EXAMPLES=False \
    --env AIRFLOW__CORE__SQL_ALCHEMY_CONN=mysql+pymysql://airflow:airflow@af-mysql.airflow/airflow \
    --command -- airflow db init

kubectl run airflow-create-user \
    --restart=Never -ti --rm --image-pull-policy=Never \
    --image=my/airflow \
    --env AIRFLOW__CORE__LOAD_EXAMPLES=False \
    --env AIRFLOW__CORE__SQL_ALCHEMY_CONN=mysql+pymysql://airflow:airflow@af-mysql.airflow/airflow \
    --command -- airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin

kubectl run airflow -n airflow -ti --rm --restart=Never --image=my/airflow --overrides='
{
  "spec": {
    "serviceAccountName": "airflow",
    "containers":[{
      "name": "webserver",
      "image": "my/airflow",
      "imagePullPolicy":"IfNotPresent",
      "command": ["airflow","webserver"],
      "stdin": true,
      "tty": true,
      "env": [
        {"name":"AIRFLOW__CORE__LOAD_EXAMPLES","value":"False"},
        {"name":"AIRFLOW__CORE__SQL_ALCHEMY_CONN","value":"mysql+pymysql://airflow:airflow@af-mysql.airflow/airflow"},
        {"name":"AIRFLOW__CORE__EXECUTOR","value":"LocalExecutor"},
        {"name":"AIRFLOW__WEBSERVER__SECRET_KEY","value":"airflow-playground"},
        {"name":"AIRFLOW_CONN_CLICKHOUSE_TEST","value":"clickhouse://analytics:admin@clickhouse-repl-05.chns:9000/test"}
      ],
      "volumeMounts": [{"mountPath": "/var/lib/airflow/dags","name": "store"}]
    },{
      "name": "scheduler",
      "image": "my/airflow",
      "imagePullPolicy":"IfNotPresent",
      "command": ["airflow","scheduler"],
      "stdin": true,
      "tty": true,
      "env": [
        {"name":"AIRFLOW__CORE__LOAD_EXAMPLES","value":"False"},
        {"name":"AIRFLOW__CORE__SQL_ALCHEMY_CONN","value":"mysql+pymysql://airflow:airflow@af-mysql.airflow/airflow"},
        {"name":"AIRFLOW__CORE__EXECUTOR","value":"LocalExecutor"},
        {"name":"AIRFLOW__WEBSERVER__SECRET_KEY","value":"airflow-playground"},
        {"name":"AIRFLOW_CONN_CLICKHOUSE_TEST","value":"clickhouse://analytics:admin@clickhouse-repl-05.chns:9000/test"}
      ],
      "volumeMounts": [{"mountPath": "/var/lib/airflow/dags","name": "store"}]
    }],
    "volumes": [{"name":"store","hostPath":{"path":"'$PWD/dags'","type":"Directory"}}]
  }
}'
)
