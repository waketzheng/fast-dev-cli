#!/bin/sh -e
set -x

[ -f ../pyproject.toml ] && cd ..

SKIP_MYPY=1 pdm run fast lint
