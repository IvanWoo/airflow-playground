#!/bin/sh
set -euo pipefail

export AIRFLOW_HOME="$(pwd)/tmp"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "${BASE_DIR}")"

setup() {
    pdm run airflow db init
    mkdir -p "${AIRFLOW_HOME}/dags"
    cp -R ${REPO_DIR}/dags/ ${AIRFLOW_HOME}/dags/
}

run() {
    pdm run pytest -v tests
}

main() {
    setup
    run
}

main
