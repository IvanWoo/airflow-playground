from datetime import datetime

from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator

from my_generator.io import all_pipeline_configs


def create_dag(dag_id, default_args, schedule_interval):
    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        schedule_interval=schedule_interval,
        catchup=False,
    )
    with dag:
        start = DummyOperator(task_id="start")
        dummy = PythonOperator(
            task_id="dummy", python_callable=lambda: print("hello world")
        )
        end = DummyOperator(task_id="end")

        start >> dummy >> end
    return dag


for config in all_pipeline_configs():
    metadata = config["metadata"]
    default_args = {
        "owner": metadata["owner"],
        "retries": metadata["retries"],
        "start_date": datetime(2019, 10, 13, 15, 50),
    }

    dag_id = metadata["dag_id"]

    globals()[dag_id] = create_dag(dag_id, default_args, metadata["cron"])
