from fast_dev_cli import __version__
from fast_dev_cli.cli import get_current_version, version


def test_version(capsys):
    version()
    assert get_current_version(is_poetry=False) in capsys.readouterr().out
    assert get_current_version(is_poetry=False) == __version__
    assert get_current_version(is_poetry=True) == ""
    assert get_current_version() == __version__
