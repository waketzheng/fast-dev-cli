import os
import re
import shutil
import subprocess
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from fast_dev_cli.cli import (
    TOML_FILE,
    BumpUp,
    EnvError,
    Exit,
    Project,
    ShellCommandError,
    StrEnum,
    bump,
    bump_version,
    capture_cmd_output,
    get_current_version,
    run_and_echo,
)

from .utils import chdir, mock_sys_argv, prepare_poetry_project


def test_enum():
    class A(StrEnum):
        ABCD = "ABCD"
        aBcD = "aBcD"
        abcd = "abcd"
        ab = "cd"

    assert A.ab == "cd"
    assert A.aBcD == "aBcD"
    assert A.abcd == "abcd"
    assert A.ABCD == "ABCD"


def _bump_commands(
    version: str, filename=TOML_FILE, emoji=False, add_sync=False
) -> tuple[str, str, str]:
    cmd = rf'bumpversion --parse "(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)" --current-version="{version}"'
    suffix = " --commit && git push && git push --tags && git log -1"
    if emoji:
        suffix = suffix.replace("--commit", "--commit --message-emoji=1")
    if add_sync:
        cmd = "pdm sync --prod && " + cmd
    patch_without_commit = cmd + f" patch {filename} --allow-dirty"
    patch_with_commit = cmd + f" patch {filename}" + suffix
    minor_with_commit = cmd + f" minor {filename} --tag" + suffix
    return patch_without_commit, patch_with_commit, minor_with_commit


def test_bump_dry(mocker):
    mocker.patch("fast_dev_cli.cli.Project.manage_by_poetry", return_value=True)
    with pytest.raises(ShellCommandError):
        get_current_version()
    mocker.patch("fast_dev_cli.cli.Project.manage_by_poetry", return_value=False)
    version = get_current_version()
    patch_without_commit, patch_with_commit, minor_with_commit = _bump_commands(
        version, filename="fast_dev_cli/__init__.py"
    )
    assert BumpUp(part="patch", commit=False, dry=True).gen() == patch_without_commit
    assert BumpUp(part="patch", commit=True, dry=True).gen() == patch_with_commit
    assert BumpUp(part="minor", commit=True, dry=True).gen() == minor_with_commit


def test_bump(
    # Use pytest-mock to mock user input
    # https://github.com/pytest-dev/pytest-mock
    mocker: MockerFixture,
    # Use tmp_path fixture, so we no need to teardown files after test
    # https://docs.pytest.org/en/latest/how-to/tmp_path.html
    tmp_path: Path,
):
    version = get_current_version()
    patch_without_commit, patch_with_commit, minor_with_commit = _bump_commands(
        version, "fast_dev_cli/__init__.py"
    )
    stream = StringIO()
    with redirect_stdout(stream):
        assert (
            BumpUp(part="patch", commit=False, dry=True).gen() == patch_without_commit
        )
        assert BumpUp(part="patch", commit=True, dry=True).gen() == patch_with_commit
        assert BumpUp(part="minor", commit=True, dry=True).gen() == minor_with_commit
        with pytest.raises(Exit):
            BumpUp(part="invalid value", commit=False).gen()
    assert "Invalid part:" in stream.getvalue()
    mocker.patch("builtins.input", return_value="1")
    assert BumpUp(part="", commit=False, dry=True).gen() == patch_without_commit
    mocker.patch("builtins.input", return_value=" ")
    assert BumpUp(part="", commit=False, dry=True).gen() == patch_without_commit
    with redirect_stdout(stream):
        BumpUp(part="patch", commit=False, dry=True).run()
    assert patch_without_commit in stream.getvalue()


def test_bump_with_poetry(mocker, tmp_poetry_project, tmp_path):
    mocker.patch("builtins.input", return_value=" ")
    version = get_current_version(check_version=False)
    patch_without_commit, patch_with_commit, minor_with_commit = _bump_commands(
        version, add_sync=False
    )
    stream = StringIO()
    with redirect_stdout(stream):
        BumpUp(part="patch", commit=False, no_sync=True).run()
    assert f"Current version(@{TOML_FILE}):" in stream.getvalue()
    stream = StringIO()
    with redirect_stdout(stream):
        BumpUp(part="minor", commit=False, no_sync=True).run()
    assert "You may want to pin tag by `fast tag`" in stream.getvalue()
    stream = StringIO()
    new_version = get_current_version()
    with redirect_stdout(stream):
        bump_version(BumpUp.PartChoices.patch, commit=False, dry=True, no_sync=True)
    assert patch_without_commit.replace(version, new_version) in stream.getvalue()
    stream = StringIO()
    with redirect_stdout(stream), mock_sys_argv(["patch", "--dry", "--no-sync"]):
        bump()
    assert patch_without_commit.replace(version, new_version) in stream.getvalue()
    stream = StringIO()
    with (
        redirect_stdout(stream),
        mock_sys_argv(["patch", "--commit", "--dry", "--no-sync"]),
    ):
        bump()
    assert patch_with_commit.replace(version, new_version) in stream.getvalue()
    stream = StringIO()
    with (
        redirect_stdout(stream),
        mock_sys_argv(["-c", "minor", "--commit", "--dry", "--no-sync"]),
    ):
        bump()
    assert minor_with_commit.replace(version, new_version) in stream.getvalue()
    text = Project.load_toml_text()
    assert new_version in text
    d = tmp_path / "temp_directory"
    d.mkdir()
    with chdir(d):
        work_dir = Project.get_work_dir()
        work_dir2 = Project.get_work_dir(TOML_FILE)
        assert Path.cwd() == d
        sub = d / ("1/" * Project.path_depth)
        sub.mkdir(parents=True, exist_ok=True)
        with chdir(sub):
            with pytest.raises(EnvError):
                Project.get_work_dir(TOML_FILE)
            assert Project.get_work_dir(allow_cwd=True) == Path.cwd()
    assert work_dir == work_dir2 == tmp_path


def test_bump_with_emoji(mocker, tmp_path, monkeypatch):
    mocker.patch("fast_dev_cli.cli.Project.manage_by_poetry", return_value=True)
    with pytest.raises(ShellCommandError):
        get_current_version()
    mocker.patch("fast_dev_cli.cli.Project.manage_by_poetry", return_value=False)
    version = get_current_version()
    patch_without_commit, patch_with_commit, minor_with_commit = _bump_commands(
        version, filename="fast_dev_cli/__init__.py", emoji=True
    )
    last_commit = "📝 Update release notes"
    mocker.patch(
        "fast_dev_cli.cli.BumpUp.get_last_commit_message",
        return_value=last_commit,
    )
    assert BumpUp(part="patch", commit=False, dry=True).gen() == patch_without_commit
    assert BumpUp(part="patch", commit=True, dry=True).gen() == patch_with_commit
    assert BumpUp(part="minor", commit=True, dry=True).gen() == minor_with_commit


def test_bump_with_emoji_in_poetry_project(mocker, tmp_path, monkeypatch):
    # real bump
    last_commit = "📝 Update release notes"
    _, patch_with_commit, __ = _bump_commands("0.1.0", emoji=True, add_sync=False)
    with prepare_poetry_project(tmp_path):
        subprocess.run(["git", "init"])
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "config", "user.name", "sb"])
        subprocess.run(["git", "config", "user.email", "sb@foo.com"])
        assert BumpUp.should_add_emoji() is False
        subprocess.run(["git", "commit", "-m", last_commit])
        monkeypatch.setenv("DONT_GIT_PUSH", "1")
        command = BumpUp(part="patch", commit=True, no_sync=True).gen()
        expected = patch_with_commit.split("&&")[0].strip().replace('""', '"0.1.0"')
        assert expected == command
        subprocess.run(["poetry", "run", "pip", "install", "bumpversion2"])
        subprocess.run(["fast", "bump", "patch", "--commit"])
        out = capture_cmd_output(["git", "log"])
        assert BumpUp.should_add_emoji()
        Path("a.txt").touch()
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "no emoji"])
        assert BumpUp.should_add_emoji() is False
    new_commit = "⬆️  Bump version: 0.1.0 → 0.1.1"
    assert new_commit in out


def test_bump_with_uv(tmp_path):
    project_dir = tmp_path / "helloworld"
    project_dir.mkdir()
    with chdir(project_dir):
        subprocess.run(["uv", "init"])
        command = BumpUp(part="patch", commit=False).gen()
        assert "pyproject.toml" in command
        Path(TOML_FILE).write_text("[project]" + os.linesep + 'version = "0.1.0"')
        command = BumpUp(part="patch", commit=True).gen()
        assert TOML_FILE in command


def test_parse_filename(tmp_path):
    pyproject = """
[tool.poetry]
version = "0"
    """
    project_dir = tmp_path / "helloworld"
    project_dir.mkdir()
    with chdir(project_dir):
        toml_file = project_dir.joinpath(TOML_FILE)
        toml_file.write_text(pyproject)
        src_dir = project_dir / project_dir.name
        src_dir.mkdir()
        init_file = src_dir / "__init__.py"
        init_file.write_text('__version__ = "0.1.0"')
        another_dir = project_dir / "hello"
        another_dir.mkdir()
        shutil.copy(init_file, another_dir / init_file.name)
        assert BumpUp.parse_filename() == "helloworld/__init__.py"
        toml_file.write_text(pyproject.strip() + '\npackages=[{include="hello"}]')
        assert BumpUp.parse_filename() == "hello/__init__.py"
        toml_file.write_text(
            pyproject.strip() + '\npackages=[{include="hello",from="py"}]'
        )
        from_dir = project_dir / "py"
        from_dir.mkdir()
        shutil.move(another_dir, from_dir)
        assert BumpUp.parse_filename() == "py/hello/__init__.py"


PDM_DYNAMIC_VERSION = """
[tool.pdm.version]
source = "file"
path = "app/__init__.py"
"""


@pytest.fixture
def dynamic_pdm_project(tmp_work_dir):
    py = "{}.{}".format(*sys.version_info)
    project = "my-project"
    capture_cmd_output(f"pdm new {project} --non-interactive --python={py} --no-git")
    with chdir(project):
        toml_file = Path("pyproject.toml")
        content = toml_file.read_text().replace(
            'version = "0.1.0"', 'dynamic = ["version"]'
        )
        toml_file.write_text(content + PDM_DYNAMIC_VERSION)
        app = Path("app")
        app.mkdir()
        yield app


def test_pdm_project(dynamic_pdm_project):
    init_file = dynamic_pdm_project / "__init__.py"
    init_file.write_text('__version__ = "0.2.0"')
    out = capture_cmd_output("fast bump patch")
    assert str(init_file) in out
    assert "0.2.1" in init_file.read_text()
    run_and_echo("git init")
    shutil.copy(Path(__file__).parent.parent / ".gitignore", ".")
    run_and_echo("git add .")
    run_and_echo("git config user.name xxx")
    run_and_echo("git config user.email xxx@a.com")
    run_and_echo('git commit -m "xxx"')
    out = capture_cmd_output("fast bump patch --emoji --commit")
    assert "--message-emoji=1" in out
    assert "⬆️  Bump version: 0.2.1 → 0.2.2" in capture_cmd_output("git log")


def test_installed_version_is_0_0_0(dynamic_pdm_project):
    version_file = dynamic_pdm_project / "__init__.py"
    version_file.write_text('__version__ = "0.0.0"')
    toml_file = Path("pyproject.toml")
    text = toml_file.read_text()
    toml_file.write_text(re.sub(r"(distribution = )false", r"\1true", text))
    capture_cmd_output("pdm install")
    version_file.write_text('__version__ = "0.3.0"')
    out = capture_cmd_output("fast bump patch")
    assert str(version_file) in out
    assert "0.3.1" in version_file.read_text()


def test_hatch_project(tmp_work_dir):
    project_name = "httpx"
    Path(project_name).mkdir()
    with chdir(project_name):
        toml_file = Path("pyproject.toml")
        toml_file.write_text("""
[build-system]
requires = ["hatchling", "hatch-fancy-pypi-readme"]
build-backend = "hatchling.build"

[project]
name = "httpx"
description = "The next generation HTTP client."
license = "BSD-3-Clause"
requires-python = ">=3.8"
authors = [
    { name = "Tom Christie", email = "tom@tomchristie.com" },
]
dependencies = [
    "certifi",
    "httpcore==1.*",
    "anyio",
    "idna",
]
dynamic = ["readme", "version"]

[tool.hatch.version]
path = "httpx/__version__.py"
        """)
        Path(project_name).mkdir()
        version_file = Path("httpx/__version__.py")
        version_file.write_text("""
__title__ = "httpx"
__description__ = "A next generation HTTP client, for Python 3."
__version__ = "0.28.1"
        """)
        out = capture_cmd_output("fast bump patch")
        assert str(version_file) in out
        assert "0.28.2" in version_file.read_text()


def test_package_project_diff(tmp_work_dir):
    project_name = "tortoise-database-url"
    package_name = "database_url"
    Path(project_name).mkdir()
    with chdir(project_name):
        Path(package_name).mkdir()
        version_file = Path(package_name, "__init__.py")
        version_file.write_text('__version__ = "0.3.0"')
        toml_file = Path("pyproject.toml")
        toml_file.write_text("""
[project]
name = "tortoise-database-url"
description = "Make it easy to generate database url."
authors = [{name="Waket Zheng", email="waketzheng@gmail.com"}]
readme = "README.md"
dynamic = ["version"]
keywords = ["database_url", "tortoise-orm"]
requires-python = ">=3.9"
dependencies = []

[tool.pdm.version]
source = "file"
path = "database_url/__init__.py"

[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"
        """)
        out = capture_cmd_output("fast bump patch")
        assert str(version_file) in out
        assert "0.3.1" in version_file.read_text()


def test_version_file_in_work_dir(tmp_work_dir):
    project_name = package_name = "bigmodels"
    Path(project_name).mkdir()
    with chdir(project_name):
        Path(package_name).mkdir()
        version_file = Path("__version__.py")
        version_file.write_text('__version__ = "0.3.0"')
        toml_file = Path("pyproject.toml")
        toml_file.write_text("""
[project]
name = "bigmodels"
description = ""
authors = [{name="Waket Zheng", email="waketzheng@gmail.com"}]
readme = "README.md"
dynamic = ["version"]
keywords = []
requires-python = ">=3.9"
dependencies = []

[tool.pdm]
distribution = false

[tool.pdm.version]
source = "file"
path = "__version__.py"

[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"
        """)
        out = capture_cmd_output("fast bump patch")
        assert str(version_file) in out
        assert "0.3.1" in version_file.read_text()
