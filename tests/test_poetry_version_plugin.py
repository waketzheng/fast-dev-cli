import shutil
import sys
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import pytest

from fast_dev_cli.cli import (
    TOML_FILE,
    BumpUp,
    ParseError,
    poetry_module_name,
    run_and_echo,
)

from .utils import chdir

CONF = """

[tool.poetry-plugin-version]
source = "init"
"""
CONF_2 = """

[tool.poetry-dynamic-versioning]
enable = true
"""


@contextmanager
def _prepare_package(
    package_path: Path, define_include=False, mark="0"
) -> Generator[Path, None, None]:
    toml_file = package_path / TOML_FILE
    package_name = poetry_module_name(package_path.name)
    init_file = package_path / package_name / "__init__.py"
    a, b = 'version = "0.1.0"', f'version = "{mark}"'
    if define_include:
        b += f'\npackages = [{{include = "{package_name}"}}]'
    with chdir(package_path.parent):
        run_and_echo(f'poetry new "{package_path.name}"')
    src_dir = package_path / "src"
    if is_src_layout := src_dir.exists():
        # poetry v2 default to use src/<package_name> layout
        init_file = src_dir / package_name / init_file.name
    toml_file.unlink()
    py_version = "{}.{}".format(*sys.version_info)
    with chdir(package_path):
        run_and_echo(f'poetry init --python="^{py_version}" --no-interaction')
        text = toml_file.read_text().replace(a, b)
        if " " in package_path.name:
            text = text.replace(
                f'name = "{package_path.name}"', f'name = "{package_name}"'
            )
        toml_file.write_text(text + CONF)
        if package_path.name != package_name:
            if is_src_layout:
                shutil.move(src_dir / package_path.name, src_dir / package_name)
            else:
                shutil.move(package_path.name, package_name)
        init_file.write_text('__version__ = "0.0.1"\n')
        yield init_file


def _build_bump_cmd(init_file: Path, project_path: Path) -> str:
    relative_path = init_file.relative_to(project_path).as_posix()
    return rf'bumpversion --parse "(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)" --current-version="0.0.1" patch {relative_path} --allow-dirty'


def test_version_plugin(tmp_path: Path) -> None:
    project_path = tmp_path / "helloworld"
    with _prepare_package(project_path) as init_file:
        command = _build_bump_cmd(init_file, project_path)
        assert BumpUp(part="patch", commit=False, dry=True).gen() == command
        run_and_echo("poetry run fast bump patch")
        assert init_file.read_text() == '__version__ = "0.0.2"\n'
        init_file.unlink()
        with pytest.raises(ParseError, match=r"Version file not found!.*"):
            BumpUp(part="patch", commit=False, dry=True).gen()


def test_version_plugin_2(tmp_path: Path) -> None:
    project_path = tmp_path / "helloworld"
    with _prepare_package(project_path, mark="0.0.0") as init_file:
        command = _build_bump_cmd(init_file, project_path)
        assert BumpUp(part="patch", commit=False, dry=True).gen() == command
        run_and_echo("poetry run fast bump patch")
        assert init_file.read_text() == '__version__ = "0.0.2"\n'
        init_file.unlink()
        with pytest.raises(ParseError, match=r"Version file not found!.*"):
            BumpUp(part="patch", commit=False, dry=True).gen()


def test_version_plugin_include_defined(tmp_path: Path) -> None:
    project_path = tmp_path / "hello world"
    with _prepare_package(project_path, True) as init_file:
        command = _build_bump_cmd(init_file, project_path)
        assert BumpUp(part="patch", commit=False, dry=True).gen() == command
        run_and_echo("poetry run fast bump patch")
        assert init_file.read_text() == '__version__ = "0.0.2"\n'


def test_version_plugin_include_defined_2(tmp_path: Path) -> None:
    project_path = tmp_path / "hello world"
    with _prepare_package(project_path, True, mark="0.0.0") as init_file:
        command = _build_bump_cmd(init_file, project_path)
        assert BumpUp(part="patch", commit=False, dry=True).gen() == command
        run_and_echo("poetry run fast bump patch")
        assert init_file.read_text() == '__version__ = "0.0.2"\n'
