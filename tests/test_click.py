import importlib
import sys
from contextlib import chdir
from pathlib import Path

import pytest
from click.core import Group
from tests.utils import mock_sys_argv


def test_click(mocker):
    mocker.patch.dict(sys.modules, {"typer": None})
    with mock_sys_argv(["lint"]), chdir(Path(__file__).parent.parent):
        cli = importlib.import_module("fast_dev_cli.cli")
        importlib.reload(cli)

        assert cli.run_and_echo("python fast_dev_cli/cli.py lint") == 0
        assert (
            cli.run_and_echo("python fast_dev_cli/cli.py lint tests fast_dev_cli") == 0
        )
        assert type(cli.cli) is Group
        with pytest.raises(TypeError):
            cli.make_style("", dry=True)
        with pytest.raises(SystemExit):
            cli.make_style("")


def test_click_lint_multi_files(mocker):
    mocker.patch.dict(sys.modules, {"typer": None})
    with mock_sys_argv(["lint", "tests", "fast_dev_cli"]), chdir(
        Path(__file__).parent.parent
    ):
        cli = importlib.import_module("fast_dev_cli.cli")
        importlib.reload(cli)
        with pytest.raises(SystemExit):
            cli.make_style()
