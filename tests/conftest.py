from pathlib import Path

import pytest

from fast_dev_cli.cli import TOML_FILE

from .utils import chdir

# toml file content before migrate to pdm
TOML_CONTENT = """
[tool.poetry]
name = "fast-dev-cli"
version = "0.8.0"
description = ""
authors = ["Waket Zheng <waketzheng@gmail.com>"]
readme = "README.md"
packages = [{include = "fast_dev_cli"}]

[tool.poetry.dependencies]
python = "^3.10"
click = ">=7.1.1"  # Many package depends on click, so only limit min version
strenum = {version = ">=0.4.15", python = "<3.11"}
type-extensions = {version = ">=0.1.2", python = "<3.11"}
coverage = {version = ">=6.5.0", optional = true}
ruff = {version = "^0.4.4", optional = true}
mypy = {version = "^1.10.0", optional = true}
bumpversion = {version = "^0.6.0", optional = true}
pytest = {version = "^8.2.0", optional = true}
typer = {version = "^0.12.3", optional = true}

[tool.poetry.extras]
all = ["ruff", "typer", "mypy", "bumpversion", "pytest", "coverage"]

[tool.poetry.group.dev.dependencies]
coveralls = {version = ">=4.0.0", python = ">=3.10,<3.13"}
coverage = ">=6.5.0"  # use >= to compare with coveralls
typer = "^0.12.3"
ruff = "^0.4.4"
mypy = "^1.10.0"
pytest = "^8.2.0"
ipython = "^8.24.0"
bumpversion = "^0.6.0"
pytest-mock = "^3.14.0"
type-extensions = "^0.1.2"
strenum = "^0.4.15"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""


@pytest.fixture
def tmp_poetry_project(tmp_path: Path):
    with chdir(tmp_path):
        tmp_path.joinpath(TOML_FILE).write_text(TOML_CONTENT)
        yield
