from contextlib import chdir
from pathlib import Path

import pytest
from tests.utils import capture_stdout, mock_sys_argv

from fast_dev_cli.cli import LintCode, capture_cmd_output, lint, make_style, only_check


@pytest.fixture
def mock_no_fix(monkeypatch):
    monkeypatch.setenv("NO_FIX", "1")


@pytest.fixture
def mock_skip_mypy(monkeypatch):
    monkeypatch.setenv("SKIP_MYPY", "1")


def test_check():
    command = capture_cmd_output("fast check --dry")
    assert (
        "isort --check-only --src=fast_dev_cli . && " in command
        and "black --check --fast . && " in command
        and "ruff check . && " in command
        and "mypy ." in command
    )


def test_lint_cmd():
    command = capture_cmd_output("poetry run python fast_dev_cli/cli.py lint . --dry")
    assert (
        capture_cmd_output("poetry run python fast_dev_cli/cli.py lint --dry")
        == capture_cmd_output("poetry run fast lint --dry")
        == command
    )
    assert (
        "isort --src=fast_dev_cli . && " in command
        and "black . && " in command
        and "ruff check --fix . && " in command
        and "mypy ." in command
    )
    assert (
        capture_cmd_output("poetry run python fast_dev_cli/cli.py lint .")
        == capture_cmd_output("poetry run python fast_dev_cli/cli.py lint")
        == capture_cmd_output("poetry run fast lint")
    )


def test_make_style(mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    with capture_stdout() as stream:
        make_style(".", check_only=False, dry=True)
    assert (
        "isort --src=fast_dev_cli . && black . && ruff check --fix . && mypy ."
        in stream.getvalue()
    )
    with capture_stdout() as stream:
        make_style(".", check_only=True, dry=True)
    assert (
        "isort --check-only --src=fast_dev_cli . && black --check --fast . && ruff check . && mypy ."
        in stream.getvalue()
    )
    with capture_stdout() as stream:
        only_check(dry=True)
    assert (
        "isort --check-only --src=fast_dev_cli . && black --check --fast . && ruff check . && mypy ."
        in stream.getvalue()
    )


def test_lint_class(mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    assert LintCode(".").gen() == (
        "isort --src=fast_dev_cli . && black . && ruff check --fix . && mypy ."
    )
    check = LintCode(".", check_only=True)
    assert check.gen() == (
        "isort --check-only --src=fast_dev_cli . && black --check --fast . && ruff check . && mypy ."
    )
    mocker.patch("fast_dev_cli.cli.Project.work_dir", return_value=None)
    assert LintCode(".").gen() == (
        "isort --src=fast_dev_cli . && black . && ruff check --fix . && mypy ."
    )


def test_lint_func(mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    with capture_stdout() as stream:
        lint(".", dry=True)
    assert (
        "isort --src=fast_dev_cli . && black . && ruff check --fix . && mypy ."
        in stream.getvalue()
    )
    with mock_sys_argv(["tests"]), capture_stdout() as stream:
        lint(dry=True)
    assert (
        "isort --src=fast_dev_cli tests && black tests && ruff check --fix tests && mypy tests"
        in stream.getvalue()
    )


def test_lint_without_black_installed(mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    mocker.patch(
        "fast_dev_cli.cli.LintCode.check_lint_tool_installed", return_value=False
    )
    with capture_stdout() as stream:
        lint(".", dry=True)
    output = stream.getvalue()
    cmd = 'python -m pip install -U "fast_dev_cli[all]"'
    tip = "You may need to run the following command to install lint tools"
    assert cmd in output and tip in output
    assert f"{tip}:\n\n  {cmd}" in output


def test_no_fix(mock_no_fix, mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    assert LintCode(".").gen() == (
        "isort --src=fast_dev_cli . && black . && ruff check . && mypy ."
    )


def test_skip_mypy(mock_skip_mypy, mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    assert LintCode(".").gen() == (
        "isort --src=fast_dev_cli . && black . && ruff check --fix ."
    )


def test_not_in_root(mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    root = Path(__file__).parent.parent
    with chdir(root / "fast_dev_cli"):
        assert (
            LintCode(".").gen()
            == "isort --src=. . && black . && ruff check --fix . && mypy ."
        )
    with chdir(root / "tests"):
        assert (
            LintCode(".").gen()
            == "isort --src=../fast_dev_cli . && black . && ruff check --fix . && mypy ."
        )
        sub = Path("temp_dir")
        sub.mkdir()
        with chdir(sub):
            cmd = LintCode(".").gen()
        sub.rmdir()
        assert (
            cmd
            == "isort --src=../../fast_dev_cli . && black . && ruff check --fix . && mypy ."
        )
