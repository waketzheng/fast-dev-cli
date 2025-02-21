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
	@pdm update --verbose

deps:
	@pdm install --verbose

_check:
	./scripts/check.py
check: deps _build _check

_lint:
	pdm run fast lint
lint: deps _build _lint

_test:
	./scripts/test.py
test: deps _test

_style:
	./scripts/format.py
style: deps _style

_build:
	rm -fR dist/
	pdm build
	BUILD_PACKAGE=fastdevcli-slim pdm build
build: deps _build

# Usage::
#   make venv version=3.12
venv:
	@echo "--> pdm venv create ${version}"
	@pdm venv create $(version)

venv39:
	@pdm venv create 3.9

venv313:
	$(MAKE) venv version=3.13
