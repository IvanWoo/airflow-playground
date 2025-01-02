# airflow-playground <!-- omit in toc -->

[Apache Airflow](https://airflow.apache.org) is an open-source workflow management platform for data engineering pipelines.

In this repo, we are using the [Kubernetes](https://kubernetes.io/) to deploy the Airflow service and other systems.

- [prerequisites](#prerequisites)
- [local development](#local-development)
  - [export requirements](#export-requirements)
  - [dag integration tests](#dag-integration-tests)
- [preparation](#preparation)
- [setup](#setup)
  - [namespace](#namespace)
  - [mysql](#mysql)
- [start airflow](#start-airflow)
  - [create the service account](#create-the-service-account)
  - [initialize database](#initialize-database)
  - [create user](#create-user)
  - [start server](#start-server)
- [cleanup](#cleanup)
- [references](#references)

## prerequisites

- [Rancher Desktop](https://github.com/rancher-sandbox/rancher-desktop): `1.9.1`
- Kubernetes: `v1.26.15`
- kubectl `v1.26.0`
- Helm: `v3.12.1`
- [pdm](https://github.com/pdm-project/pdm): `2.22.1`

## local development

```sh
pdm install
```

### export requirements

```sh
pdm lock -S inherit_metadata
pdm export -f requirements > requirements.txt
```

### dag integration tests

```sh
pdm run test
```

## preparation

build the docker image [with proper namespace](https://github.com/rancher-sandbox/rancher-desktop/issues/952#issuecomment-1049434115)

```sh
nerdctl --namespace=k8s.io build -t my/airflow -f Dockerfile .
```

## setup

tl;dr: `./scripts/up.sh`

### namespace

```sh
kubectl create namespace airflow --dry-run=client -o yaml | kubectl apply -f -
```

### mysql

follow the [bitnami mysql chart](https://github.com/bitnami/charts/tree/master/bitnami/mysql) to install mysql

```sh
helm repo add bitnami https://charts.bitnami.com/bitnami
```

```sh
helm upgrade --install af-mysql bitnami/mysql -n airflow -f mysql/values.yaml
```

verify the mysql is running

```sh
kubectl exec af-mysql-0 -n airflow -- mysql -uairflow -pairflow -e "SHOW DATABASES"
```

```
Database
airflow
information_schema
```

## start airflow

tl;dr: `./scripts/run.sh`

### create the service account

```sh
kubectl apply -f airflow/rbac.yaml -n airflow
```

### initialize database

```sh
kubectl run airflow-initdb \
    --restart=Never -ti --rm --image-pull-policy=Never \
    --image=my/airflow \
    --env AIRFLOW__CORE__LOAD_EXAMPLES=False \
    --env AIRFLOW__CORE__SQL_ALCHEMY_CONN=mysql+pymysql://airflow:airflow@af-mysql.airflow/airflow \
    --command -- airflow db init
```

verify the database is initialized

```sh
kubectl exec af-mysql-0 -n airflow -- mysql -uairflow -pairflow -e "SHOW TABLES IN airflow"
```

```
Tables_in_airflow
ab_permission
ab_permission_view
ab_permission_view_role
ab_register_user
ab_role
ab_user
ab_user_role
ab_view_menu
alembic_version
callback_request
connection
dag
dag_code
dag_owner_attributes
dag_pickle
dag_run
dag_run_note
dag_schedule_dataset_reference
dag_tag
dag_warning
dagrun_dataset_event
dataset
dataset_dag_run_queue
dataset_event
import_error
job
log
log_template
rendered_task_instance_fields
serialized_dag
session
sla_miss
slot_pool
task_fail
task_instance
task_instance_note
task_map
task_outlet_dataset_reference
task_reschedule
trigger
variable
xcom
```

### create user

```sh
kubectl run airflow-create-user \
    --restart=Never -ti --rm --image-pull-policy=Never \
    --image=my/airflow \
    --env AIRFLOW__CORE__LOAD_EXAMPLES=False \
    --env AIRFLOW__CORE__SQL_ALCHEMY_CONN=mysql+pymysql://airflow:airflow@af-mysql.airflow/airflow \
    --command -- airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin
```

### start server

```sh
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
```

verify by checking the dags

```sh
kubectl exec -ti airflow -n airflow -c webserver -- airflow dags list
```

view the [webserver portal](http://localhost:8080/)

```sh
kubectl port-forward airflow -n airflow 8080
```

## cleanup

tl;dr: `./scripts/down.sh`

```sh
kubectl delete po --all -n airflow
helm uninstall af-mysql -n airflow
kubectl delete pvc --all -n airflow
kubectl delete -f airflow/rbac.yaml -n airflow
kubectl delete namespace airflow
```

## references

- [stwind/airflow-on-kubernetes](https://github.com/stwind/airflow-on-kubernetes): Bare Minimal Airflow On Kubernetes
- [astronomer/airflow-testing-skeleton](https://github.com/astronomer/airflow-testing-skeleton)
