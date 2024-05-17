#!/usr/bin/env bash

set -e
set -x

[ -f ../pyproject.toml ] && cd ..

pdm run fast check || \
  echo -e "\033[1m Please run './scripts/format.sh' to auto-fix style issues \033[0m"
