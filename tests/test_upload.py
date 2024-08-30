from fast_dev_cli.cli import upload


def test_upload(capsys):
    upload(dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "poetry publish --build"
