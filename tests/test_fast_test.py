import pathlib

from pytest_mock import MockerFixture
from tests.utils import capture_stdout

from fast_dev_cli.cli import capture_cmd_output, test


def test_test(mocker):
    output = capture_cmd_output("python fast_dev_cli/cli.py test --dry")
    assert (
        "coverage run -m pytest -s && " in output
        and 'coverage report --omit="tests/*" -m' in output
    )

    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    with capture_stdout() as stream:
        test(dry=True)
    assert (
        'coverage run -m pytest -s && coverage report --omit="tests/*" -m'
        in stream.getvalue()
    )


def test_test_with_poetry_run(mocker: MockerFixture):
    mocker.patch("fast_dev_cli.cli.check_call", return_value=False)
    with capture_stdout() as stream:
        test(dry=True)
    assert (
        '--> poetry run coverage run -m pytest -s && poetry run coverage report --omit="tests/*" -m'
        in stream.getvalue()
    )


def test_test_no_in_venv(mocker: MockerFixture):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=False)
    with capture_stdout() as stream:
        test(dry=True)
    assert (
        '--> poetry run coverage run -m pytest -s && poetry run coverage report --omit="tests/*" -m'
        in stream.getvalue()
    )


def test_run_script(mocker: MockerFixture, capsys):
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=True)
    test(dry=True)
    assert "sh scripts/test.sh" in capsys.readouterr().out


def test_run_script_in_sub_directory(mocker: MockerFixture, capsys):
    parent = pathlib.Path(__file__).parent
    mocker.patch("fast_dev_cli.cli._should_run_test_script", return_value=True)
    mocker.patch("pathlib.Path.cwd", return_value=parent)
    test(dry=True)
    out = capsys.readouterr().out
    assert f"cd {parent.parent} && sh scripts/test.sh" in out
