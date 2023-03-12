import pytest
from airflow.models import DagBag

from dags.my_generator.io import get_all_dag_ids


@pytest.fixture()
def dagbag():
    return DagBag(include_examples=False)


@pytest.fixture()
def all_generated_dag_ids():
    return get_all_dag_ids()


def assert_dag_dict_equal(source, dag):
    assert dag.task_dict.keys() == source.keys()
    for task_id, downstream_list in source.items():
        assert dag.has_task(task_id)
        task = dag.get_task(task_id)
        assert task.downstream_task_ids == set(downstream_list)


def test_dagbag(dagbag):
    assert dagbag.import_errors == {}


@pytest.mark.parametrize(
    "dag_id",
    [
        "clickhouse_demo",
        "foobar",
    ],
)
def test_dag_loaded(dagbag, dag_id):
    dag = dagbag.get_dag(dag_id=dag_id)
    assert dag is not None


def test_generated_dag_loaded(dagbag, all_generated_dag_ids):
    for dag_id in all_generated_dag_ids:
        dag = dagbag.get_dag(dag_id=dag_id)
        assert dag is not None, f"DAG {dag_id} not loaded"


def test_no_duplicate_dag_ids(all_generated_dag_ids):
    assert len(set(all_generated_dag_ids)) == len(all_generated_dag_ids)


@pytest.mark.parametrize(
    "dag_id, expected_task_dict",
    [
        (
            "foobar",
            {
                "foo": ["bar"],
                "bar": ["pod_foo"],
                "pod_foo": [],
            },
        ),
        (
            "clickhouse_demo",
            {
                "sales_distributed": ["print_sales_distributed"],
                "print_sales_distributed": [],
            },
        ),
        (
            "1",
            {
                "start": ["dummy"],
                "dummy": ["end"],
                "end": [],
            },
        ),
    ],
)
def test_dag(dagbag, dag_id, expected_task_dict):
    dag = dagbag.get_dag(dag_id=dag_id)
    assert_dag_dict_equal(expected_task_dict, dag)
