# ChangeLog

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
