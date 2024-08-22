help:
	@echo  "FastDevCli development makefile"
	@echo
	@echo  "usage: make <target>"
	@echo  "Targets:"
	@echo  "    up      Updates dev/test dependencies"
	@echo  "    deps    Ensure dev/test dependencies are installed"
	@echo  "    check	Checks that build is sane"
	@echo  "    test	Runs all tests"
	@echo  "    style   Auto-formats the code"

up:
	@pdm update

deps:
	@pdm install --dev --with=all

_check:
	./scripts/check.sh
check: deps _build _check

_lint:
	./scripts/format.sh
lint: deps _build _lint

_test:
	./scripts/test.sh
test: deps _test

_style:
	ruff format .
	ruff check --fix .
style: deps _style

_build:
	rm -fR dist/
	pdm build
	BUILD_PACKAGE=fastdevcli-slim pdm build
build: deps _build
