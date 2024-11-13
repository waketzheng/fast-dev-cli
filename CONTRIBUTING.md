# Contributing

## Install pdm
```shell
pipx install pdm
```
- See more at:
https://pdm-project.org/latest/#installation

## Set up environment
```shell
git clone git@github.com:waketzheng/fast-dev-cli.git
cd fast-dev-cl
```
- Create virtual environment and install dependencies by pdm
```shell
# Create virtual environment
pdm use 3

# Activate virtual environment
source .venv/*/activate  # for Linux/MacOS/GitBash
.venv\Scripts\activate  # For Windows

# Install dependenices
python -m ensurepip
python -m pip install --upgrade pip
pdm export --without-hashes -o dev_requirements.txt
python -m pip install -r dev_requirements.txt
python -m pip install -e .
```
## Lint code
```shell
./scripts/format.py
```
## Check
```shell
./scripts/check.py
```
## Test
```shell
pipx install poetry
pipx inject poetry poetry-plugin-version
# or: pdm run python -m pip install poetry poetry-plugin-version
./scripts/test.py
```
