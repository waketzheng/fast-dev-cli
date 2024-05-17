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
    StrEnum,
    bump,
    bump_version,
    get_current_version,
)
from tests.utils import mock_sys_argv

from .utils import chdir


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


def _bump_commands(version: str, filename=TOML_FILE) -> tuple[str, str, str]:
    cmd = rf'bumpversion --parse "(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)" --current-version="{version}"'
    suffix = " --commit && git push && git push --tags && git log -1"
    patch_without_commit = cmd + f" patch {filename} --allow-dirty"
    patch_with_commit = cmd + f" patch {filename}" + suffix
    minor_with_commit = cmd + f" minor {filename} --tag" + suffix
    return patch_without_commit, patch_with_commit, minor_with_commit


def test_bump_dry(mocker):
    mocker.patch("fast_dev_cli.cli.Project.manage_by_poetry", return_value=True)
    version = get_current_version()
    patch_without_commit, patch_with_commit, minor_with_commit = _bump_commands(version)
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
        version, "fast_dev_cli/cli.py"
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
    version = get_current_version()
    patch_without_commit, patch_with_commit, minor_with_commit = _bump_commands(version)
    stream = StringIO()
    with redirect_stdout(stream):
        BumpUp(part="patch", commit=False).run()
    assert f"Current version(@{TOML_FILE}):" in stream.getvalue()
    stream = StringIO()
    with redirect_stdout(stream):
        BumpUp(part="minor", commit=False).run()
    assert "You may want to pin tag by `fast tag`" in stream.getvalue()
    stream = StringIO()
    new_version = get_current_version()
    with redirect_stdout(stream):
        bump_version(BumpUp.PartChoices.patch, commit=False, dry=True)
    assert patch_without_commit.replace(version, new_version) in stream.getvalue()
    stream = StringIO()
    with redirect_stdout(stream), mock_sys_argv(["patch", "--dry"]):
        bump()
    assert patch_without_commit.replace(version, new_version) in stream.getvalue()
    stream = StringIO()
    with redirect_stdout(stream), mock_sys_argv(["patch", "--commit", "--dry"]):
        bump()
    assert patch_with_commit.replace(version, new_version) in stream.getvalue()
    stream = StringIO()
    with (
        redirect_stdout(stream),
        mock_sys_argv(["-c", "minor", "--commit", "--dry"]),
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
