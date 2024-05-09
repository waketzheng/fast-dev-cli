import pathlib

from pytest_mock import MockerFixture

from fast_dev_cli.cli import capture_cmd_output
from fast_dev_cli.cli import test as unitcase


def test_test(mocker, capsys):
    output = capture_cmd_output("python fast_dev_cli/cli.py test --dry")
    assert (
        "coverage run -m pytest -s && " in output
        and 'coverage report --omit="tests/*" -m' in output
    )

    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    unitcase(dry=True)
    assert (
        'coverage run -m pytest -s && coverage report --omit="tests/*" -m'
        in capsys.readouterr().out
    )


def test_test_with_poetry_run(mocker: MockerFixture, capsys):
    mocker.patch("fast_dev_cli.cli.check_call", return_value=False)
    unitcase(dry=True)
    assert (
        '--> poetry run coverage run -m pytest -s && poetry run coverage report --omit="tests/*" -m'
        in capsys.readouterr().out
    )


def test_test_no_in_venv(mocker: MockerFixture, capsys):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=False)
    unitcase(dry=True)
    assert (
        '--> poetry run coverage run -m pytest -s && poetry run coverage report --omit="tests/*" -m'
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
