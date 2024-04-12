from fast_dev_cli.cli import get_current_version, version


def test_version(capsys):
    version()
    assert get_current_version() in capsys.readouterr().out
