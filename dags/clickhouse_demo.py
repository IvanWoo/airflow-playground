from airflow import DAG
from airflow_clickhouse_plugin.operators.clickhouse import ClickHouseOperator
from airflow.operators.python import PythonOperator
from datetime import datetime

default_args = {
    "start_date": datetime(2015, 6, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
}

with DAG(
    dag_id="clickhouse_demo",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:
    t1 = ClickHouseOperator(
        task_id="sales_distributed",
        database="test",
        sql=(
            """
            SELECT count() FROM sales_distributed
            """,
            # result of the last query is pushed to XCom
        ),
        clickhouse_conn_id="clickhouse_test",
    )
    t2 = PythonOperator(
        task_id="print_sales_distributed",
        provide_context=True,
        python_callable=lambda task_instance, **_:
        # pulling XCom value and printing it
        print(task_instance.xcom_pull(task_ids="sales_distributed")),
    )

    t1 >> t2
