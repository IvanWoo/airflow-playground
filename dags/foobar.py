from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from datetime import datetime

AIRFLOW_K8S_NAMESPACE = "airflow"

default_args = {
    "start_date": datetime(2015, 6, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
}

with DAG(
    "foobar", default_args=default_args, schedule_interval=None, catchup=False
) as dag:
    t1 = BashOperator(task_id="foo", bash_command="echo foo", do_xcom_push=True)
    t2 = BashOperator(task_id="bar", bash_command="echo bar")
    t3 = KubernetesPodOperator(
        namespace=AIRFLOW_K8S_NAMESPACE,
        image="busybox",
        image_pull_policy="IfNotPresent",
        arguments=["echo", "inside the pod: {{ ti.xcom_pull(task_ids='foo') }}"],
        name="busybox-test",
        task_id="pod_foo",
        is_delete_operator_pod=True,
        get_logs=True,
        in_cluster=True,
        dag=dag,
    )

    t1 >> t2 >> t3
