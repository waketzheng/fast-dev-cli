import importlib
import sys

from tests.utils import mock_sys_argv


def test_pad_dot():
    with mock_sys_argv(["lint"]):
        cli = importlib.import_module("fast_dev_cli.cli")
        assert callable(cli.cli)
        importlib.reload(cli)
        assert sys.argv[1:] == ["lint", "."]
