#!/usr/bin/env bash
set -euxo pipefail
export SIOTLS_INTEGRATION=1
uv run coverage run --source src/ --branch -m unittest discover --quiet
uv run coverage xml --quiet
uvx --with defusedxml genbadge coverage --input-file coverage.xml --silent
