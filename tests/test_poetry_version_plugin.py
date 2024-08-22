from pathlib import Path

import pytest

from fast_dev_cli.cli import (
    TOML_FILE,
    BumpUp,
    ParseError,
    run_and_echo,
)

from .utils import chdir

CONF = """

[tool.poetry-version-plugin]
source = "init"
"""


def test_version_plugin(tmp_path: Path) -> None:
    package_path = tmp_path / "helloworld"
    toml_file = package_path / TOML_FILE
    init_file = package_path / package_path.name / "__init__.py"
    a, b = 'version = "0.1.0"', 'version = "0"'
    with chdir(tmp_path):
        run_and_echo(f"poetry new {package_path.name}")
    with chdir(package_path):
        text = toml_file.read_text().replace(a, b)
        toml_file.write_text(text + CONF)
        init_file.write_text('__version__ = "0.0.1"\n')
        assert (
            BumpUp(part="patch", commit=False, dry=True).gen()
            == 'bumpversion --parse "(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+)" --current-version="0.0.1" patch helloworld/__init__.py --allow-dirty'
        )
        run_and_echo("poetry run fast bump patch")
        assert init_file.read_text() == '__version__ = "0.0.2"\n'
        init_file.unlink()
        with pytest.raises(ParseError, match=r"Version file not found!.*"):
            BumpUp(part="patch", commit=False, dry=True).gen()


def test_version_plugin_include_defined(tmp_path: Path) -> None:
    package_path = tmp_path / "hello world"
    toml_file = package_path / TOML_FILE
    package_name = package_path.name.replace(" ", "_")
    init_file = package_path / package_name / "__init__.py"
    a, b = 'version = "0.1.0"', 'version = "0"'
    b += '\npackages = [{include = "%s"}]' % package_name
    with chdir(tmp_path):
        run_and_echo(f"poetry new '{package_path.name}'")
    with chdir(package_path):
        text = toml_file.read_text().replace(a, b)
        toml_file.write_text(text + CONF)
        run_and_echo(f"mv '{package_path.name}' {package_name}")
        init_file.write_text('__version__ = "0.0.1"\n')
        assert (
            BumpUp(part="patch", commit=False, dry=True).gen()
            == f'bumpversion --parse "(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+)" --current-version="0.0.1" patch {package_name}/__init__.py --allow-dirty'
        )
        run_and_echo("poetry run fast bump patch")
        assert init_file.read_text() == '__version__ = "0.0.2"\n'
