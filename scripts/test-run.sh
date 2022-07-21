#!/bin/sh
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "${BASE_DIR}")"

run() {
    pdm run pytest -v tests
}

main() {
    run
}

main
