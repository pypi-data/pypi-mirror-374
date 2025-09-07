#!/usr/bin/env bash
set -euxo pipefail
SIOTLS_INTEGRATION=1
SIOTLS_SLOW=1
uv run unittest-xml-reporting --output-file .coverage.unittest.xml
uv run coverage run --source src/ --branch -m unittest
uv run coverage xml
uvx --with defusedxml genbadge tests -i .coverage.unittest.xml
uvx --with defusedxml genbadge coverage -i coverage.xml
