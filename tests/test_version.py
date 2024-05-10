import subprocess

from fast_dev_cli import __version__
from fast_dev_cli.cli import get_current_version, version


def test_version(capsys):
    version()
    assert get_current_version() in capsys.readouterr().out
    r = subprocess.run(["poetry", "version", "-s"], capture_output=True)
    assert r.stdout.decode().strip() == __version__
