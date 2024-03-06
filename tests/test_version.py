from tests.utils import capture_stdout

from fast_dev_cli.cli import get_current_version, version


def test_version():
    with capture_stdout() as stream:
        version()
    assert stream.getvalue().strip() == get_current_version()
