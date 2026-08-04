# Contributing

## Install uv/rust-just/pdm
```shell
pipx install uv
uv tool install rust-just
uv tool install pdm
pdm config check_update false
```
- See more at:
https://github.com/astral-sh/uv
https://github.com/casey/just
https://pdm-project.org/latest/#installation

## Set up environment
```shell
git clone git@github.com:waketzheng/fast-dev-cli.git
cd fast-dev-cl
```
- Create virtual environment by pdm and install dependencies by uv
```shell
# Create virtual environment
just venv

# Install dependencies
just install
```
## Lint code
```shell
just lint
```
## Check
```shell
just check
```
## Test
```shell
just test
```
