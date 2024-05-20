from pathlib import Path

import pytest

from fast_dev_cli.cli import (
    TOML_FILE,
    LintCode,
    Project,
    capture_cmd_output,
    lint,
    make_style,
    only_check,
)

from .utils import capture_stdout, chdir, mock_sys_argv


@pytest.fixture
def mock_no_fix(monkeypatch):
    monkeypatch.setenv("NO_FIX", "1")


@pytest.fixture
def mock_skip_mypy(monkeypatch):
    monkeypatch.setenv("SKIP_MYPY", "1")


SEP = " && "
LINT_CMD = "ruff format . && ruff check --extend-select=I --fix . && mypy ."
CHECK_CMD = "ruff format --check . && ruff check --extend-select=I . && mypy ."


def test_check():
    command = capture_cmd_output("fast check --dry")
    for cmd in CHECK_CMD.split(SEP):
        assert cmd in command


def test_lint_cmd():
    run = "pdm run "
    lint_cmd = f"{run}python fast_dev_cli/cli.py lint"
    command = capture_cmd_output(f"{lint_cmd} . --dry")
    for cmd in LINT_CMD.split(SEP):
        assert cmd in command
    assert (
        capture_cmd_output(f"{lint_cmd} --dry")
        == capture_cmd_output(f"{run}fast lint --dry")
        == command
    )
    assert (
        capture_cmd_output(f"{lint_cmd} .")
        == capture_cmd_output(f"{lint_cmd} lint")
        == capture_cmd_output(f"{run}fast lint")
    )


def test_make_style(mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    with capture_stdout() as stream:
        make_style(["."], check_only=False, dry=True)
    assert LINT_CMD in stream.getvalue()
    with capture_stdout() as stream:
        make_style(["."], check_only=True, dry=True)
    assert CHECK_CMD in stream.getvalue()
    with capture_stdout() as stream:
        only_check(dry=True)
    assert CHECK_CMD in stream.getvalue()


def test_lint_class(mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    assert LintCode(".").gen() == LINT_CMD
    check = LintCode(".", check_only=True)
    assert check.gen() == CHECK_CMD
    mocker.patch("fast_dev_cli.cli.Project.work_dir", return_value=None)
    assert LintCode(".").gen() == LINT_CMD


def test_lint_func(mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    with capture_stdout() as stream:
        lint(".", dry=True)
    assert LINT_CMD in stream.getvalue()
    with mock_sys_argv(["tests"]), capture_stdout() as stream:
        lint(dry=True)
    assert LINT_CMD.replace(" .", " tests") in stream.getvalue()


def test_lint_without_ruff_installed(mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    mocker.patch(
        "fast_dev_cli.cli.LintCode.check_lint_tool_installed", return_value=False
    )
    with capture_stdout() as stream:
        lint(".", dry=True)
    output = stream.getvalue()
    cmd = 'python -m pip install -U "fast_dev_cli"'
    assert cmd in output
    tip = "You may need to run following command to install lint tools"
    assert tip in output
    assert f"{tip}:\n\n  {cmd}" in output


def test_no_fix(mock_no_fix, mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    assert LintCode(".").gen() == LINT_CMD.replace(" --fix", "")


def test_skip_mypy(mock_skip_mypy, mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    cmds = LINT_CMD.split(SEP)
    assert LintCode(".").gen() == SEP.join(i for i in cmds if not i.startswith("mypy"))


def test_not_in_root(mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    root = Path(__file__).parent.parent
    with chdir(root / "fast_dev_cli"):
        assert LintCode(".").gen() == LINT_CMD
    with chdir(root / "tests"):
        assert LintCode(".").gen() == LINT_CMD
        sub = Path("temp_dir")
        sub.mkdir()
        with chdir(sub):
            cmd = LintCode(".").gen()
        sub.rmdir()
        assert cmd == LINT_CMD


def test_get_manage_tool(tmp_path):
    with chdir(tmp_path):
        try:
            Project.get_manage_tool()
        except Exception as e:
            assert e.__class__.__name__ == "EnvError"
        Path(TOML_FILE).write_text("[tool.poetry]")
        assert Project.get_manage_tool() == "poetry"
        Path(TOML_FILE).write_text("[tool.pdm]")
        assert Project.get_manage_tool() == "pdm"
