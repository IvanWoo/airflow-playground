import os
import pathlib
import shutil

import pytest

ROOT_DIR = pathlib.Path(__file__).parent.parent.absolute()

os.environ["AIRFLOW__CORE__LOAD_DEFAULT_CONNECTION"] = "False"
os.environ["AIRFLOW__CORE__LOAD_EXAMPLES"] = "False"
os.environ["AIRFLOW__CORE__UNIT_TEST_MODE"] = "True"
os.environ["AIRFLOW_HOME"] = str(ROOT_DIR)


@pytest.fixture(autouse=True, scope="session")
def reset_db():
    from airflow.utils import db

    db.resetdb()
    yield

    # cleanup temp files generated during tests
    files = ["unittests.cfg", "unittests.db", "webserver_config.py"]
    for file in files:
        os.remove(ROOT_DIR / file)

    folders = ["logs"]
    for folder in folders:
        shutil.rmtree(ROOT_DIR / folder)
