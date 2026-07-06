#!/usr/bin/env -S just --justfile
# ^ A shebang isn't required, but allows a justfile to be executed
#   like a script, with `./justfile lint`, for example.

# NOTE: You can run the following command to install `just`:
#   uv tool install rust-just

system-info:
    @echo "This is an {{ arch() }} machine running on {{ os_family() }}"
    just --list

# Use powershell for Windows so that 'Git Bash' and 'PyCharm Terminal' get the same result
set windows-powershell
PY_EXEC := if os_family() == "windows" { ".venv/Scripts/python.exe" } else { ".venv/bin/python" }
PROJECT_NAME := file_name(justfile_directory())
SRC := if path_exists("src") == "true" { "src" } else { replace(PROJECT_NAME, "-", "_") }

_venv_create *args:
    pdm venv create --with-pip {{ args }}

_uv_venv *args:
    @just _venv_create --with uv {{ args }}

_win_venv *args:
    if (Test-Path '~/AppData/Roaming/uv/tools/rust-just') { just _uv_venv {{ args }}} else { just _venv_create {{ args }}}

[unix]
venv *args:
    @if test ! -e .venv; then just _uv_venv {{ args }}; fi
[windows]
venv *args:
    @if (-Not (Test-Path '.venv')) { just _win_venv {{ args }}}

_venv313 *args:
    @just venv 3.13 {{ args }}

# Change registry in uv.lock to be pypi.org
pypi *args:
    @uv run --no-sync fast pypi --quiet {{ args }}

# Update the registry in `uv.lock` to use the mirror set by the config.
_pypi_reverse *args:
    @just pypi --reverse {{ args }}

_pdm_deps *args:
    pdm install --frozen -G :all {{ args }}

_uv_sync *args:
    uv sync --all-extras --all-groups {{ args }}

_uv_deps *args:
    @just _pypi_reverse
    @just _uv_sync --reinstall-package={{ PROJECT_NAME }} {{ args }}
    @just pypi

# Install dependencies
[unix]
install *args: venv
    @just _uv_deps {{ args }}
[windows]
install *args: venv
    if (Test-Path '~/AppData/Roaming/uv/tools/rust-just') { echo 'uv sync ...'; just _uv_deps {{ args }} } else { echo 'Using pdm ...'; just _pdm_deps {{ args }} }

alias deps := install

_uv_lock *args:
    @just _pypi_reverse
    uv lock {{ args }}
    @just _uv_deps --frozen

_win_lock *args:
    @if (-Not (Test-Path 'pdm.lock')) { echo 'No pdm lock file, skip locking!' } else { pdm lock -G :all {{ args }} }

[unix]
lock *args: venv
    @just _uv_lock {{ args }}
[windows]
lock *args: venv
    if (Test-Path '~/AppData/Roaming/uv/tools/rust-just') { echo 'uv lock...'; just _uv_lock {{ args }} } else { just _win_lock {{ args }}}

_pypi_wrap_uv *args:
    @just _pypi_reverse
    uv {{ args }}
    @just pypi

# Run `uv add` to update deps and keep register to be pypi.org
add *args: venv
    @just _pypi_wrap_uv add {{ args }}

# Run `uv remove` to update deps and keep register to be pypi.org
remove *args: venv
    @just _pypi_wrap_uv remove {{ args }}

_win_up *args:
    @if (-Not (Test-Path 'pdm.lock')) { echo 'No pdm lock file, only install deps without update lock...'; just _pdm_deps {{ args }}  } else { pdm update -G :all {{ args }} }

[unix]
up *args: venv
    @just _uv_lock --upgrade {{ args }}
[windows]
up *args: venv
    if (Test-Path '~/AppData/Roaming/uv/tools/rust-just') { echo 'uv lock...'; just _uv_lock --upgrade {{ args }} } else { just _win_up {{ args }} }

_uv_clear *args:
    @just _uv_sync {{ args }}

[unix]
clear *args:
    @just _uv_clear {{ args }}
[windows]
clear *args:
    @if (-Not (Test-Path 'pdm.lock')) { just _uv_clear {{ args }}  } else { pdm sync -G :all --clean {{ args }} }

_uvx_py *args:
    uvx --python={{ PY_EXEC }} {{ args }}

mypy path=(SRC) *args:
    @just _uvx_py mypy --python-executable={{ PY_EXEC }} {{ path }} {{ args }}

_mypy310 path=(SRC) *args:
    uv export --python=3.10 --no-hashes --all-extras --all-groups --frozen -o dev_requirements.txt
    uvx --python=3.10 --with-requirements=dev_requirements.txt mypy --cache-dir=.mypy310_cache {{ path }} {{ args }}

right path=(SRC) *args:
    @just _uvx_py pyright --pythonpath={{ PY_EXEC }} {{ path }} {{ args }}

_format *args:
    just --fmt
    pdm run fast lint --ty {{ args }}

_codeqc *args:
    just --evaluate
    @just mypy {{ args }}
    @just right {{ args }}

_lint *args:
    @just _format --bandit {{ args }}
    @just _codeqc {{ args }}

lint *args: install
    @just _lint {{ args }}

# make style without installing deps
fmt *args:
    @just _format --skip-mypy {{ args }}

alias _style := fmt

# install deps and make style
style *args: install
    @just fmt {{ args }}

_check *args:
    pdm run fast check --ty {{ args }}
    @just _codeqc {{ args }}

# install deps and check style
check *args: install
    @just _check {{ args }}

_build *args:
    uv build --offline --clear {{ args }}

build *args: install
    pdm build {{ args }}

_test *args:
    pdm run fast test {{ args }}

test *args: install
    @just _test {{ args }}

prod *args: venv
    uv sync --no-dev {{ args }}

_uv_pip *args:
    uv pip install {{ args }}

[unix]
pipi *args: venv
    @just _uv_pip {{ args }}
[windows]
pipi *args: venv
    @if (-Not (Test-Path '.venv/Scripts/pip.exe')) { just _uv_pip {{ args }} } else { pdm run pip install {{ args }} }

_install_me:
    @just pipi -e .

start:
    prek install
    @just deps

version part="patch" *args:
    pdm run fast bump {{ part }} {{ args }}

bump *args:
    @just version patch --commit {{ args }}

tag *args:
    pdm run fast tag {{ args }}

_log:
    git --no-pager log -1

# Bump version with patch part(0.1.1->0.1.2) and auto mark tag
release: venv bump tag _log

# Bump version with minor part(0.1.1->0.2.0) and auto mark tag
minor *args:
    @just version minor --commit {{ args }}
    @just _log
