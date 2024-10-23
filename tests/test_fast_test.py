import os
import pathlib
from typing import Generator

import pytest
from pytest_mock import MockerFixture

from fast_dev_cli.cli import (
    Project,
    _should_run_test_script,
    capture_cmd_output,
    coverage_test,
)
from fast_dev_cli.cli import test as unitcase

TEST_SCRIPT = os.path.join("scripts", "test.py")


@pytest.fixture
def script_path() -> Generator[pathlib.Path, None, None]:
    parent = pathlib.Path(__file__).parent
    test_script = parent.resolve().parent / "scripts" / "test.py"
    yield test_script


def test_cli_test(mocker, capsys):
    output = capture_cmd_output("python fast_dev_cli/cli.py test --dry --ignore-script")
    assert (
        "coverage run -m pytest -s && " in output
        and 'coverage report --omit="tests/*" -m' in output
    )

    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=None)
    unitcase(dry=True)
    assert (
        'coverage run -m pytest -s && coverage report --omit="tests/*" -m'
        in capsys.readouterr().out
    )


def test_test_with_pdm_run(mocker: MockerFixture, capsys):
    mocker.patch("fast_dev_cli.cli.check_call", return_value=False)
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=None)
    unitcase(dry=True)
    assert (
        '--> pdm run coverage run -m pytest -s && pdm run coverage report --omit="tests/*" -m'
        in capsys.readouterr().out
    )


def test_test_with_poetry_or_pdm_run(mocker: MockerFixture, capsys):
    mocker.patch("fast_dev_cli.cli.check_call", return_value=False)
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=None)
    mocker.patch("fast_dev_cli.cli.Project.manage_by_poetry", return_value=True)
    unitcase(dry=True)
    command = "coverage"
    if tool := Project.get_manage_tool():
        command = tool + " run " + command
    assert (
        f'--> {command} run -m pytest -s && {command} report --omit="tests/*" -m'
        in capsys.readouterr().out
    )


def test_test_not_in_venv(mocker: MockerFixture, capsys):
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=None)
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=False)
    unitcase(dry=True)
    command = "coverage"
    if tool := Project.get_manage_tool():
        command = tool + " run " + command
    assert (
        f'--> {command} run -m pytest -s && {command} report --omit="tests/*" -m'
        in capsys.readouterr().out
    )


def test_run_script(mocker: MockerFixture, capsys, script_path):
    assert _should_run_test_script()
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=script_path)
    unitcase(dry=True)
    assert TEST_SCRIPT in capsys.readouterr().out
    assert _should_run_test_script(pathlib.Path("not-exist")) is None


def test_ignore_script(mocker: MockerFixture, capsys, script_path):
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=script_path)
    unitcase(dry=True, ignore_script=True)
    assert TEST_SCRIPT not in capsys.readouterr().out


def test_run_script_in_sub_directory(mocker: MockerFixture, capsys, script_path):
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=script_path)
    mocker.patch("pathlib.Path.cwd", return_value=script_path.parent)
    unitcase(dry=True)
    out = capsys.readouterr().out
    assert f"cd {script_path.parent.parent} && {TEST_SCRIPT}" in out


def test_fast_test(mocker, capsys):
    output = capture_cmd_output("fast test --dry --ignore-script")
    assert (
        "coverage run -m pytest -s && " in output
        and 'coverage report --omit="tests/*" -m' in output
    )

    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=None)
    coverage_test(dry=True)
    assert (
        'coverage run -m pytest -s && coverage report --omit="tests/*" -m'
        in capsys.readouterr().out
    )
