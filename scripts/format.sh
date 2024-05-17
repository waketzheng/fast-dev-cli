#!/bin/sh -e
set -x

[ -f ../pyproject.toml ] && cd ..

pdm run fast lint
