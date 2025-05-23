from __future__ import annotations

import shutil
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
    run_and_echo,
)

from .utils import capture_stdout, chdir, mock_sys_argv


@pytest.fixture
def mock_no_fix(monkeypatch):
    monkeypatch.setenv("NO_FIX", "1")


@pytest.fixture
def mock_skip_mypy(monkeypatch):
    monkeypatch.setenv("SKIP_MYPY", "1")


@pytest.fixture
def mock_skip_mypy_0(monkeypatch):
    monkeypatch.setenv("SKIP_MYPY", "0")


@pytest.fixture
def mock_no_dmypy(monkeypatch):
    monkeypatch.setenv("NO_DMYPY", "1")


@pytest.fixture
def mock_no_dmypy_0(monkeypatch):
    monkeypatch.setenv("NO_DMYPY", "0")


@pytest.fixture
def mock_ignore_missing_imports(monkeypatch):
    monkeypatch.setenv("IGNORE_MISSING_IMPORTS", "1")


@pytest.fixture
def mock_ignore_missing_imports_0(monkeypatch):
    monkeypatch.setenv("IGNORE_MISSING_IMPORTS", "0")


SEP = " && "
_CMD = "ruff format{} . && ruff check --extend-select=I,B,SIM{} . && mypy ."
LINT_CMD = _CMD.format("", " --fix")
CHECK_CMD = _CMD.format(" --check", "")


def test_check(mock_no_dmypy, monkeypatch, mocker):
    command = capture_cmd_output("fast check --dry")
    for cmd in CHECK_CMD.split(SEP):
        assert cmd in command
    command2 = capture_cmd_output("fast check --bandit --dry")
    assert command2 == command + " && bandit -c pyproject.toml -r ."
    monkeypatch.setenv("FASTDEVCLI_BANDIT", "1")
    command3 = capture_cmd_output("fast check --dry")
    assert command3 == command2
    monkeypatch.setenv("FASTDEVCLI_BANDIT", "0")
    command4 = capture_cmd_output("fast check --dry")
    assert command4 == command


def test_check_bandit(tmp_path):
    package_path = tmp_path / "foo"
    with chdir(tmp_path):
        assert LintCode.get_package_name() == "."
        run_and_echo(f"poetry new {package_path.name}")
    src_dir = package_path / "src"
    if not src_dir.exists():  # For poetry<2.1
        src_dir = src_dir.parent / package_path.name
    with chdir(package_path):
        package_name = src_dir.name
        assert f"bandit -r {package_name}" in LintCode.to_cmd(bandit=True)
        toml_file = Path(TOML_FILE)
        content = toml_file.read_text()
        toml_file.write_text(content + '\n[tool.bandit]\nexclude_dirs = ["tests"]')
        assert f"bandit -c {TOML_FILE} -r ." in LintCode.to_cmd(bandit=True)
    shutil.rmtree(src_dir)
    with chdir(package_path):
        assert LintCode.get_package_name() == "."
        command = capture_cmd_output("fast check --bandit --dry")
        assert f"bandit -c {TOML_FILE} -r ." in command
        toml_file.write_text(content)
        command = capture_cmd_output("fast check --bandit --dry")
        assert "bandit -r ." in command


def test_check_skip_mypy(mock_skip_mypy_0, mocker, capsys):
    cmd = "fast check --skip-mypy --dry"
    cmd2 = "fast lint --check-only --skip-mypy --dry"
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    command = capture_cmd_output(cmd)
    command2 = capture_cmd_output(cmd2)
    expected = "--> " + SEP.join(
        filter(lambda i: not i.startswith("mypy"), CHECK_CMD.split(SEP))
    )
    assert command == command2 == expected


def test_fast_check():
    _fast_check()


def test_fast_check_0(mock_no_dmypy_0):
    _fast_check()


def _fast_check():
    command = capture_cmd_output("fast check --dry")
    for cmd in CHECK_CMD.split(SEP):
        assert cmd in command


def test_lint_cmd(mock_no_dmypy):
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
        == capture_cmd_output(f"{lint_cmd}")
        == capture_cmd_output(f"{run}fast lint")
    )


def test_lint_html():
    run = "pdm run "
    lint_cmd = f"{run}python fast_dev_cli/cli.py lint"
    command = capture_cmd_output(f"{lint_cmd} index.html --dry")
    assert "prettier -w index.html" in command
    command = capture_cmd_output(f"{lint_cmd} index.html flv.html --dry")
    assert "prettier -w index.html flv.html" in command
    cmd = "fast lint index.html --dry"
    assert "prettier -w index.html" in capture_cmd_output(cmd)
    assert "prettier -w index.html" in capture_cmd_output("pdm run " + cmd)
    cmd = "fast lint index.html flv.html --dry"
    assert "prettier -w index.html flv.html" in capture_cmd_output(cmd)
    assert "prettier -w index.html flv.html" in capture_cmd_output("pdm run " + cmd)
    assert LintCode.to_cmd("index.html") == "prettier -w index.html"
    assert LintCode.to_cmd("index.html flv.html") == "prettier -w index.html flv.html"


def test_lint_by_global_fast():
    run = "pdm run "
    fast = Path.home() / ".local" / "bin" / "fast"
    command = capture_cmd_output(f"{fast} lint --dry")
    for cmd in command.split(SEP):
        assert run in cmd


def test_with_dmypy():
    cmd = "fast lint --dmypy --dry ."
    assert "dmypy run ." in capture_cmd_output(cmd)
    assert "dmypy run ." in capture_cmd_output("pdm run " + cmd)
    command = LintCode.to_cmd(use_dmypy=True, tool="pdm")
    assert "dmypy run ." in command
    command = LintCode.to_cmd(use_dmypy=False, tool="pdm")
    assert "dmypy run ." not in command


def test_dmypy_run(monkeypatch):
    command = capture_cmd_output("python -m fast_dev_cli lint --dry .")
    assert "dmypy run ." not in command
    monkeypatch.setenv("FASTDEVCLI_DMYPY", "1")
    command = capture_cmd_output("python -m fast_dev_cli lint --dry .")
    assert "dmypy run ." in command
    command = capture_cmd_output("python -m fast_dev_cli lint --skip-mypy --dry .")
    assert "dmypy run ." not in command


def test_lint_with_prefix(mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=False)
    with capture_stdout() as stream:
        make_style(["."], check_only=False, dry=True)
    assert "pdm run" in stream.getvalue()


def test_make_style(mock_skip_mypy_0, mocker, mock_no_dmypy):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    with capture_stdout() as stream:
        make_style(check_only=False, dry=True)
    assert LINT_CMD in stream.getvalue()
    with capture_stdout() as stream:
        make_style(["."], check_only=False, dry=True)
    assert LINT_CMD in stream.getvalue()
    with capture_stdout() as stream:
        make_style(".", check_only=False, dry=True)  # type:ignore[arg-type]
    assert LINT_CMD in stream.getvalue()
    with capture_stdout() as stream:
        make_style(["."], check_only=True, dry=True)
    assert CHECK_CMD in stream.getvalue()
    with capture_stdout() as stream:
        only_check(dry=True)
    assert CHECK_CMD in stream.getvalue()


def test_lint_class(mocker, mock_no_dmypy):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    assert LintCode(".").gen() == LINT_CMD
    check = LintCode(".", check_only=True)
    assert check.gen() == CHECK_CMD
    mocker.patch("fast_dev_cli.cli.Project.work_dir", return_value=None)
    assert LintCode(".").gen() == LINT_CMD


def test_lint_func(mocker, mock_no_dmypy):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    with capture_stdout() as stream:
        lint(".", dry=True)
    assert LINT_CMD in stream.getvalue()
    with mock_sys_argv(["tests"]), capture_stdout() as stream:
        lint(dry=True)
    assert LINT_CMD.replace(" .", " tests") in stream.getvalue()
    with capture_stdout() as stream:
        lint(["lint"], dry=True)
    assert LINT_CMD in stream.getvalue()
    assert LINT_CMD in capture_cmd_output("pdm run python -m fast_dev_cli lint --dry")


def test_lint_without_ruff_installed(mocker, mock_no_dmypy):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    mocker.patch(
        "fast_dev_cli.cli.LintCode.check_lint_tool_installed", return_value=False
    )
    with capture_stdout() as stream:
        lint(".", dry=True)
    output = stream.getvalue()
    cmd = 'python -m pip install -U "fast-dev-cli"'
    assert cmd in output
    tip = "You may need to run following command to install lint tools"
    assert tip in output
    assert f"{tip}:\n\n  {cmd}" in output


def test_no_fix(mock_no_fix, mocker, mock_no_dmypy):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    assert LintCode(".").gen() == LINT_CMD.replace(" --fix", "")


def test_skip_mypy(mock_skip_mypy, mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    cmds = LINT_CMD.split(SEP)
    assert LintCode(".").gen() == SEP.join(i for i in cmds if not i.startswith("mypy"))


def test_skip_mypy_option(mock_skip_mypy_0, mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    cmds = LINT_CMD.split(SEP)
    assert LintCode(".", skip_mypy=True).gen() == SEP.join(
        i for i in cmds if not i.startswith("mypy")
    )


def test_skip_mypy_fast_lint(mock_skip_mypy_0, mocker, capsys):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    command = capture_cmd_output("fast lint --skip-mypy --dry")
    cmds = LINT_CMD.split(SEP)
    assert command.replace("--> ", "") == SEP.join(
        i for i in cmds if not i.startswith("mypy")
    )


def test_skip_mypy_0(mock_skip_mypy_0, mocker, mock_no_dmypy):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    assert LintCode(".").gen() == LINT_CMD


def test_ignore_missing_imports(mock_ignore_missing_imports, mocker, mock_no_dmypy):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    assert LintCode(".").gen() == LINT_CMD.replace(
        "mypy ", "mypy --ignore-missing-imports "
    )


def test_ignore_missing_imports_0(mock_ignore_missing_imports_0, mocker, mock_no_dmypy):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    assert LintCode(".").gen() == LINT_CMD


def test_not_in_root(mocker, mock_no_dmypy):
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
        Path(TOML_FILE).write_text("[tool.uv]")
        assert Project.get_manage_tool() == "uv"


class TestGetPackageName:
    project = "hello-world"

    def test_get_package_name(self, tmp_path):
        project_dir = tmp_path / self.project
        project_dir.mkdir()
        module_name = project_dir.name.replace("-", "_").replace(" ", "_")
        with chdir(project_dir):
            Path(TOML_FILE).touch()
            Path(module_name).mkdir()
            assert LintCode.get_package_name() == module_name
            Path("src").mkdir()
            assert LintCode.get_package_name() == module_name
            shutil.rmtree(module_name)
            assert LintCode.get_package_name() == "src"


class TestGetPackageNameWithSpace(TestGetPackageName):
    project = "hello world"
