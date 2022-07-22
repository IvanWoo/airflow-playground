#!/bin/sh
set -euo pipefail

pdm list --freeze >requirements.txt
