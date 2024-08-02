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

check: deps
	./scripts/check.sh

lint: deps build
	./scripts/format.sh

test: deps
	./scripts/test.sh

style: deps
	ruff format .
	ruff check --fix .

build: deps
	rm -fR dist/
	pdm build
	BUILD_PACKAGE=fastdevcli-slim pdm build
