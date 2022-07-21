import pytest

from airflow.models import DagBag


@pytest.fixture()
def dagbag():
    return DagBag(include_examples=False)


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


@pytest.mark.parametrize(
    "dag_id, expected_task_dict",
    [
        (
            "foobar",
            {
                "foo": ["bar"],
                "bar": [],
            },
        ),
        (
            "clickhouse_demo",
            {
                "sales_distributed": ["print_sales_distributed"],
                "print_sales_distributed": [],
            },
        ),
    ],
)
def test_dag(dagbag, dag_id, expected_task_dict):
    dag = dagbag.get_dag(dag_id=dag_id)
    assert_dag_dict_equal(expected_task_dict, dag)
