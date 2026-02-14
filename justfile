#!/usr/bin/env -S just --justfile
# ^ A shebang isn't required, but allows a justfile to be executed
#   like a script, with `./justfile lint`, for example.

# NOTE: You can run the following command to install `just`:
#   uv tool install rust-just

system-info:
    @echo "This is an {{arch()}} machine running on {{os_family()}}"
    just --list

# Use powershell for Windows so that 'Git Bash' and 'PyCharm Terminal' get the same result
set windows-powershell := true
VENV_CREATE := "pdm venv create --with uv --with-pip"
PDM_DEPS := "pdm install -G :all"
UV_DEPS := "uv sync --all-extras --all-groups"
UV_PIP_I := "uv pip install"
BIN_DIR := if os_family() == "windows" { "Scripts" } else { "bin" }
PY_EXEC := if os_family() == "windows" { ".venv/Scripts/python.exe" } else { ".venv/bin/python" }

[unix]
venv *args:
    @if test ! -e .venv; then {{ VENV_CREATE }} {{ args }}; fi
[windows]
venv *args:
    @if (-Not (Test-Path '.venv')) { {{ VENV_CREATE }} {{ args }} }

venv313:
    {{ VENV_CREATE }} 3.13

uv_deps *args:
    {{ UV_DEPS }} {{args}}
    @just install_me
    @uv run --no-sync fast pypi --quiet

[unix]
deps *args: venv
    @if test ! -e uv.lock; then (if test ! -e pdm.lock; then (echo uv pip install -e .; uv pip install -e .); else (echo pdm install -G :all;pdm i -G :all); fi); else @just uv_deps; fi
[windows]
deps *args: venv
    if (-Not (Test-Path '~/AppData/Roaming/uv/tools/rust-just')) { echo 'Using pdm ...'; {{ PDM_DEPS }} {{ args }} } else { echo 'uv sync...'; just uv_deps {{ args }} }

uv_lock *args:
    uv lock {{args}}
    @just deps --frozen

[unix]
lock *args:
    @if test -e uv.lock; then just uv_lock {{ args }}; fi
    if test -e pdm.lock; then pdm lock -G :all; fi
[windows]
lock *args:
    if (-Not (Test-Path '~/AppData/Roaming/uv/tools/rust-just')) { echo 'Using pdm ...'; pdm lock -G :all {{ args }} } else { echo 'uv lock...'; just uv_lock {{ args }} }


up *args:
    @if test ! -e uv.lock; then (if test ! -e pdm.lock; then (echo Fallback to uv ...; just uv_lock --upgrade {{args}}); else (echo pdm update -G :all;pdm update -G :all {{args}}); fi); else @just uv_lock --upgrade {{args}}; fi

uv_clear *args:
    {{ UV_DEPS }} {{args}}

pdm_clear *args:
    pdm sync -G :all --clean {{args}}

[unix]
clear *args:
    @if test ! -e uv.lock; then (if test ! -e pdm.lock; then (echo Fallback to uv ...; just uv_clear {{args}}); else (echo pdm clearing...;just pdm_clear {{args}}); fi); else @just uv_clear {{args}}; fi
[windows]
clear *args:
    @if (-Not (Test-Path 'pdm.lock')) { just uv_clear {{args}}  } else { just pdm_clear {{args}} }

run *args: venv
    .venv/{{BIN_DIR}}/{{args}}

_lint *args:
    pdm run fast lint --ty {{args}}

lint *args: deps
    @just _lint {{args}}

fmt *args:
    @just _lint --skip-mypy {{args}}

alias _style := fmt

style *args: deps
    @just fmt {{args}}

_check *args:
    pdm run fast check --ty {{args}}
    @just mypy

check *args: deps
    @just _check {{args}}

_build *args:
    pdm build {{args}}

build *args: deps
    @just _build {{args}}

_test *args:
    pdm run fast test {{args}}

test *args: deps
    @just _test {{args}}


[unix]
prod *args: venv
    @if (-Not (Test-Path 'uv.lock')) { pdm i --prod {{args}} } else { uv sync {{args}} }
[windows]
prod *args: venv
    pdm i --prod {{args}}

[unix]
pipi *args: venv
    {{ UV_PIP_I }} {{args}}
[windows]
pipi *args: venv
    @if (-Not (Test-Path '.venv/Scripts/pip.exe')) { UV_PIP_I {{args}} } else { @just run pip install {{args}} }

install_me:
    @just pipi -e .

start:
    pre-commit install
    @just deps

version part="patch":
    pdm run fast bump {{part}}

bump *args:
    pdm run fast bump patch --commit {{args}}

tag *args:
    pdm run fast tag {{args}}

release: venv bump tag
    git --no-pager log -1

uvx_py *args:
    uvx --python={{PY_EXEC}} {{args}}

mypy *args:
    @just uvx_py mypy --python-executable={{PY_EXEC}} fast_dev_cli {{args}}

mypy310 *args:
    uv export --python=3.10 --no-hashes --all-extras --all-groups --no-group test --frozen -o dev_requirements.txt
    uvx --python=3.10 --with-requirements=dev_requirements.txt mypy --cache-dir=.mypy310_cache fast_dev_cli {{args}}

right *args:
    @just uvx_py pyright --pythonpath={{PY_EXEC}} fast_dev_cli {{args}}
