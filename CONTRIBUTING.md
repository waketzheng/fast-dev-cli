# Contributing

## Install pdm
```bash
pipx install pdm
```
- See more at:
https://pdm-project.org/latest/#installation

### Custom `pdm shell`:

Copy and paste the following function to your ~/.bashrc file and restart your shell.
```bash
pdm() {
  local command=$1

  if [[ "$command" == "shell" ]]; then
      eval $(pdm venv activate)
  else
      command pdm $@
  fi
}
```
Ref: https://pdm-project.org/latest/usage/venv/#activate-a-virtualenv

## Set up environment
```bash
git clone git@github.com:waketzheng/fast-dev-cli.git
cd fast-dev-cl
pdm use 3
pdm shell
pdm install
```
## Lint code
```bash
./scripts/format.py
```
## Check
```bash
./scripts/check.py
```
## Test
```bash
./scripts/unittest.py
```
