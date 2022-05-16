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
    --env AIRFLOW__CORE__SQL_ALCHEMY_CONN=mysql+pymysql://airflow:airflow@af-mysql.airflow/airflow \
    --command -- airflow db init
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
connection
dag
dag_code
dag_pickle
dag_run
dag_tag
import_error
job
log
rendered_task_instance_fields
sensor_instance
serialized_dag
session
sla_miss
slot_pool
task_fail
task_instance
task_reschedule
trigger
variable
xcom
```

create user

```sh
kubectl run airflow-create-user \
    --restart=Never -ti --rm --image-pull-policy=Never \
    --image=my/airflow \
    --env AIRFLOW__CORE__LOAD_EXAMPLES=False \
    --env AIRFLOW__CORE__SQL_ALCHEMY_CONN=mysql+pymysql://airflow:airflow@af-mysql.airflow/airflow \
    --command -- airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin
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
        {"name":"AIRFLOW__CORE__SQL_ALCHEMY_CONN","value":"mysql+pymysql://airflow:airflow@af-mysql.airflow/airflow"}, 
        {"name":"AIRFLOW__CORE__EXECUTOR","value":"LocalExecutor"},
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

### airflow-clickhouse-plugin

airflow `1.10.14` is not compatible with `airflow-clickhouse-plugin==0.5.7.post1`

get the below error when starting the server

```sh
ERROR - Failed to import plugin airflow_clickhouse_hook
Traceback (most recent call last):
  File "/usr/local/lib/python3.8/site-packages/airflow/plugins_manager.py", line 150, in load_entrypoint_plugins
    plugin_obj.__usable_import_name = entry_point.module
AttributeError: 'EntryPoint' object has no attribute 'module'
```

airflow `2.3.0` works with `airflow-clickhouse-plugin==0.8.1`
