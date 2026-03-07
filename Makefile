help:
	@echo  "FastDevCli development makefile"
	@echo
	@echo  "Usage: make <target>"
	@echo  "Targets:"
	@echo  "    up      Updates dev/test dependencies"
	@echo  "    deps    Ensure dev/test dependencies are installed"
	@echo  "    check   Checks that build is sane"
	@echo  "    test    Runs all tests"
	@echo  "    style   Auto-formats the code"
	@echo  "    lint    Auto-formats the code and check type hints"

up:
	@just up

lock:
	@just lock

deps:
	@just deps

_check:
	@just _check
	pdm run twine check dist/*
check: deps _build _check

_lint:
	@just _lint
lint: deps _build _lint

_test:
	./scripts/test.py
test: deps _test

_style:
	./scripts/format.py
style: deps _style

_build:
	@just _build

build:
	@just build

# Usage::
#   make venv version=3.12
venv:
	@just venv $(version)

venv314t:
	@just venv 3.14t

venv313:
	$(MAKE) venv version=3.13

ci: check _test
