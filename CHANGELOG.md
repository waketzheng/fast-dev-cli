# ChangeLog

## 0.17

### [0.17.3](../../releases/tag/v0.17.3) - 2025-08-26

#### Added
- Support `fast deps`

### [0.17.2](../../releases/tag/v0.17.2) - 2025-08-22

#### Added
- Support `fast list --prefix=uv`

#### Fixed
- Fix fast lint get error mypy relative path

### [0.17.1](../../releases/tag/v0.17.1) - 2025-08-17

#### Added
- Support `fast --version`
- Add '--no-sync' option for bump/tag
- Add '--emoji' option for bump

#### Changed
- `fast` get the same display with `fast --help`
- `fast lint` will not add `uv run` prefix if lint tool exists
- Only try to import emoji module when necessary
- `fast version` now display version file value when declared by tool.pdm.version section
- Remove `<tool> run` prefix for ruff if it exists

### [0.17.0](../../releases/tag/v0.17.0) - 2025-08-05

#### Added
- Support `fast exec "<cmd command>"`

#### Changed
- Only run `pdm sync --prod` when version not match

## 0.16

### [0.16.2](../../releases/tag/v0.16.2) - 2025-07-09

#### Changed
- Run `pdm sync --prod` when bump and tag for pdm project

### [0.16.1](../../releases/tag/v0.16.1) - 2025-06-06

#### Fixed
- Fix get dynacmic version error when it's defined to be '0.0.0'

### [0.16.0](../../releases/tag/v0.16.0) - 2025-06-05

#### Changed
- Move `packaging` and `emoji` to optional dependencies

## 0.15

### [0.15.2](../../releases/tag/v0.15.2) - 2025-06-05

#### Fixed
- Fix bump error with version file in work directory

### [0.15.1](../../releases/tag/v0.15.1) - 2025-05-31

#### Added
- `fast bump <part>` support hatch dynamic version

#### Changed
- Move `packaging` from dev to main dependencies

#### Fixed
- Fix bump error with pdm dynamic version

### [0.15.0](../../releases/tag/v0.15.0) - 2025-04-18

#### Added
- Support `fast lint --tool=uv`

#### Changed
- Strict type hints for `fast_dev_cli/cli.py`

#### Fixed
- Fix macOS filename auto completion error

## 0.14

### [0.14.2](../../releases/tag/v0.14.2) - 2025-04-15

#### Added
- Support `fast lint xxx.html`

### [0.14.1](../../releases/tag/v0.14.1) - 2025-04-06

#### Added
- Support `fast lint --bandit`

### [0.14.0](../../releases/tag/v0.14.0) - 2025-03-20

#### Changed
- Move 'ruff' from dependencies of fast-dev-cli to "fastdevcli-slim[all]"
- Pin ruff to ">=0.11.0"

## 0.13

### [0.13.0](../../releases/tag/v0.13.0) - 2025-03-19

#### Changed
- Prefer to use `mypy` instead of `dmypy run`

## 0.12

### [0.12.0](../../releases/tag/v0.12.0) - 2025-02-21

- Remove upper limit for python version
- Fix bump version error with src layout

## 0.11

### [0.11.6](../../releases/tag/v0.11.6) - 2025-01-12

- Limit ruff version constraint to `<1`

### [0.11.5](../../releases/tag/v0.11.5) - 2024-12-31

- Fix emptry prefix when virtual environment not activated

### [0.11.4](../../releases/tag/v0.11.4) - 2024-11-13

- Support python3.9

### [0.11.3](../../releases/tag/v0.11.3) - 2024-11-05

- Fix bump version error in uv project

### [0.11.2](../../releases/tag/v0.11.2) - 2024-11-04

- Refactor check script to make it easy to change tool
- Default to add one more space after bump up emoji
- Suppport py2 for format script

### [0.11.1](../../releases/tag/v0.11.1) - 2024-11-01

- Support `--skip-mypy` for lint/check command
- Support src/package structure for fast bump and fast tag
- Support publish by pdm/uv/twine for `fast upload`

### [0.11.0](../../releases/tag/v0.11.0) - 2024-10-29

- Support uv
- Fix `get_current_version` error
- Auto use pdm/uv to export for sync command
- Support poetry-dynamic-versioning

## 0.10

### [0.10.1](../../releases/tag/v0.10.1) - 2024-10-23

- Change script file type from sh to py
- Pass unittest at Windows
- Add contributing guide

### [0.10.0](../../releases/tag/v0.10.0) - 2024-10-22

- Support `fast check --bandit`
- `load_bool` return default when env value is not a boolean format
