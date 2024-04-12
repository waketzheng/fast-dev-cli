from fast_dev_cli.cli import upload


def test_upload(capsys):
    upload(dry=True)
    out = capsys.readouterr().out.strip()
    assert "poetry publish --build" == out.replace("--> ", "")
