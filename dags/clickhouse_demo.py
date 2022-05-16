from airflow import DAG
from airflow_clickhouse_plugin.operators.clickhouse_operator import ClickHouseOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

default_args = {
    "start_date": datetime(2015, 6, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
}

with DAG(
    dag_id="clickhouse_demo",
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
        task_id="print_month_income",
        provide_context=True,
        python_callable=lambda task_instance, **_:
        # pulling XCom value and printing it
        print(task_instance.xcom_pull(task_ids="get_count_sales")),
    )

    t1 >> t2
