# ChangeLog

## 0.21

### [0.21.0]*(Unreleased)*

#### Changed
- Use typer instead of typer-slim
- refactor: default to add `--all-groups` argument when fast sync

## 0.20

### [0.20.1](../../releases/tag/v0.20.1) - 2026-01-18

#### Changed
- refactor: not raise FileNotFoundError when `fast pypi --reverse` without uv config file

### [0.20.0](../../releases/tag/v0.20.0) - 2026-01-13

#### Added
- feat: support `fast pypi --reverse`

#### Remove
- Remove mypy from standard extra because prefer to use ty which can be install globally
- Remove bumpversion2 from standard extra as it can be install globally

## 0.19

### [0.19.9](../../releases/tag/v0.19.9) - 2026-01-06

#### Changed
- refactor: no need to with prefix for ty

### [0.19.8](../../releases/tag/v0.19.8) - 2026-01-05

#### Fixes
- fix: fast pypi not change zip package download url

### [0.19.7](../../releases/tag/v0.19.7) - 2026-01-04

#### Added
- feat: support `fast lint --ty`

#### Fixes
- fix: windows read version file raises gbk decode error

### [0.19.6](../../releases/tag/v0.19.6) - 2026-01-04

#### Added
- feat: support `fast pypi --slim`

### [0.19.5](../../releases/tag/v0.19.5) - 2025-11-25

#### Added
- feat: support `fast lint --strict`

### [0.19.4](../../releases/tag/v0.19.4) - 2025-11-20

#### Added
- feat: support `fast lint --up`

### [0.19.3](../../releases/tag/v0.19.3) - 2025-11-19

#### Added
- feat: expanduser for `run_and_echo`

### [0.19.2](../../releases/tag/v0.19.2) - 2025-11-04

#### Changed
- refactor: use `X | None` instead of `Optional[X]`
- refactor: prefer to use `uv pip` instead of `uv sync` when bump

### [0.19.1](../../releases/tag/v0.19.1) - 2025-10-16

#### Changed
- refactor: prefer to choose 'uv' for `fast deps`

### [0.19.0](../../releases/tag/v0.19.0) - 2025-10-16

#### Changed
- feat: drop support for Python3.9

## 0.18

### [0.18.6](../../releases/tag/v0.18.6) - 2025-10-16

#### Changed
- `fast lint` will not add prefix when tool is auto and virtual environment activated

### [0.18.5](../../releases/tag/v0.18.5) - 2025-09-18

#### Added
- Add `--no-sync` to `uv run` at Windows

#### Changed
- Use `pdm install --frozen` instead of `pdm sync` as it does not require the pdm.lock

#### Fixed
- Fix lint error at Windows

### [0.18.4](../../releases/tag/v0.18.4) - 2025-09-16

#### Added
- feat: support `--no-active` and `--no-inexact` for fast deps
- feat: support project version if it is not dynamic
- Auto add suffix with `fast lint <stem>`

### [0.18.3](../../releases/tag/v0.18.3) - 2025-09-12

#### Added
- Auto add suffix with `fast lint <stem>.`

### [0.18.2](../../releases/tag/v0.18.2) - 2025-09-09

#### Fixed
- Fix inexact prompt when lint without ruff installed

### [0.18.1](../../releases/tag/v0.18.1) - 2025-09-06

#### Added
- Support `fast pypi custom_uv.lock`

### [0.18.0](../../releases/tag/v0.18.0) - 2025-08-31

#### Changed
- Use `typer-slim` instead of `typer`

## 0.17

### [0.17.3](../../releases/tag/v0.17.3) - 2025-08-26

#### Added
- Support `fast deps`

### [0.17.2](../../releases/tag/v0.17.2) - 2025-08-22

#### Added
- Support `fast lint --prefix=uv`

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
