import pathlib

from pytest_mock import MockerFixture

from fast_dev_cli.cli import Project, capture_cmd_output, coverage_test
from fast_dev_cli.cli import test as unitcase


def test_cli_test(mocker, capsys):
    output = capture_cmd_output("python fast_dev_cli/cli.py test --dry --ignore-script")
    assert (
        "coverage run -m pytest -s && " in output
        and 'coverage report --omit="tests/*" -m' in output
    )

    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=False)
    unitcase(dry=True)
    assert (
        'coverage run -m pytest -s && coverage report --omit="tests/*" -m'
        in capsys.readouterr().out
    )


def test_test_with_pdm_run(mocker: MockerFixture, capsys):
    mocker.patch("fast_dev_cli.cli.check_call", return_value=False)
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=False)
    unitcase(dry=True)
    assert (
        '--> pdm run coverage run -m pytest -s && pdm run coverage report --omit="tests/*" -m'
        in capsys.readouterr().out
    )


def test_test_with_poetry_or_pdm_run(mocker: MockerFixture, capsys):
    mocker.patch("fast_dev_cli.cli.check_call", return_value=False)
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=False)
    mocker.patch("fast_dev_cli.cli.Project.manage_by_poetry", return_value=True)
    unitcase(dry=True)
    command = "coverage"
    if tool := Project.get_manage_tool():
        command = tool + " run " + command
    assert (
        '--> {0} run -m pytest -s && {0} report --omit="tests/*" -m'.format(command)
        in capsys.readouterr().out
    )


def test_test_not_in_venv(mocker: MockerFixture, capsys):
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=False)
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=False)
    unitcase(dry=True)
    command = "coverage"
    if tool := Project.get_manage_tool():
        command = tool + " run " + command
    assert (
        '--> {0} run -m pytest -s && {0} report --omit="tests/*" -m'.format(command)
        in capsys.readouterr().out
    )


def test_run_script(mocker: MockerFixture, capsys):
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=True)
    unitcase(dry=True)
    assert "sh scripts/test.sh" in capsys.readouterr().out


def test_ignore_script(mocker: MockerFixture, capsys):
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=True)
    unitcase(dry=True, ignore_script=True)
    assert "sh scripts/test.sh" not in capsys.readouterr().out


def test_run_script_in_sub_directory(mocker: MockerFixture, capsys):
    parent = pathlib.Path(__file__).parent
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=True)
    mocker.patch("pathlib.Path.cwd", return_value=parent)
    unitcase(dry=True)
    out = capsys.readouterr().out
    assert f"cd {parent.parent} && sh scripts/test.sh" in out


def test_fast_test(mocker, capsys):
    output = capture_cmd_output("fast test --dry --ignore-script")
    assert (
        "coverage run -m pytest -s && " in output
        and 'coverage report --omit="tests/*" -m' in output
    )

    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=False)
    coverage_test(dry=True)
    assert (
        'coverage run -m pytest -s && coverage report --omit="tests/*" -m'
        in capsys.readouterr().out
    )
