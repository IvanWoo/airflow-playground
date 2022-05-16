## preparation

build the docker image [with proper namespace](https://github.com/rancher-sandbox/rancher-desktop/issues/952#issuecomment-1049434115)

```sh
docker --namespace=k8s.io build -t my/airflow -f Dockerfile . 
```

## setup

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

```sh
Database
airflow
information_schema
```

initialize database

```sh
kubectl run airflow-initdb \
    --restart=Never -ti --rm --image-pull-policy=Never \
    --image=my/airflow \
    --env AIRFLOW__CORE__LOAD_EXAMPLES=False \
    --env AIRFLOW__CORE__SQL_ALCHEMY_CONN=mysql://airflow:airflow@af-mysql.airflow/airflow \
    --command -- airflow initdb
```

verify the database is initialized

```sh
kubectl exec af-mysql-0 -n airflow -- mysql -uairflow -pairflow -e "SHOW TABLES IN airflow"
```

```sh
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
chart
connection
dag
dag_code
dag_pickle
dag_run
dag_tag
import_error
job
known_event
known_event_type
kube_resource_version
kube_worker_uuid
log
rendered_task_instance_fields
serialized_dag
sla_miss
slot_pool
task_fail
task_instance
task_reschedule
users
variable
xcom
```

### start airflow

```sh
kubectl run airflow -n airflow -ti --rm --restart=Never --image=my/airflow --overrides='
{
  "spec": {
    "containers":[{
      "name": "webserver",
      "image": "my/airflow",
      "imagePullPolicy":"IfNotPresent",
      "command": ["airflow","webserver"],
      "stdin": true,
      "tty": true,
      "env": [
        {"name":"AIRFLOW__CORE__LOAD_EXAMPLES","value":"False"},
        {"name":"AIRFLOW__CORE__SQL_ALCHEMY_CONN","value":"mysql://airflow:airflow@af-mysql.airflow/airflow"}, 
        {"name":"AIRFLOW__CORE__EXECUTOR","value":"LocalExecutor"},
        {"name":"AIRFLOW__KUBERNETES__WORKER_CONTAINER_REPOSITORY","value":"my/airflow"},
        {"name":"AIRFLOW__KUBERNETES__WORKER_CONTAINER_TAG","value":"latest"},
        {"name":"AIRFLOW__KUBERNETES__DAGS_VOLUME_HOST","value":"'$PWD/dags'"},
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
        {"name":"AIRFLOW__CORE__SQL_ALCHEMY_CONN","value":"mysql://airflow:airflow@af-mysql.airflow/airflow"}, 
        {"name":"AIRFLOW__CORE__EXECUTOR","value":"LocalExecutor"},
        {"name":"AIRFLOW__KUBERNETES__WORKER_CONTAINER_REPOSITORY","value":"my/airflow"},
        {"name":"AIRFLOW__KUBERNETES__WORKER_CONTAINER_TAG","value":"latest"},
        {"name":"AIRFLOW__KUBERNETES__DAGS_VOLUME_HOST","value":"'$PWD/dags'"},
        {"name":"AIRFLOW__KUBERNETES__KUBE_CLIENT_REQUEST_ARGS","value":""},
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

view the webserver portal

```sh
kubectl port-forward airflow -n airflow 8080
```

## cleanup

```sh
kubectl delete po airflow -n airflow
helm uninstall af-mysql -n airflow
kubectl delete pvc --all -n airflow
kubectl delete namespace airflow
```

## gotcha

airflow `1.10.14` is not compatible with `airflow-clickhouse-plugin==0.5.7.post1`

get the below error when starting the server

```sh
ERROR - Failed to import plugin airflow_clickhouse_hook
Traceback (most recent call last):
  File "/usr/local/lib/python3.8/site-packages/airflow/plugins_manager.py", line 150, in load_entrypoint_plugins
    plugin_obj.__usable_import_name = entry_point.module
AttributeError: 'EntryPoint' object has no attribute 'module'
```