from fast_dev_cli.cli import dev, runserver


def test_runserver(capsys):
    runserver(dry=True)
    out = capsys.readouterr().out.strip()
    assert "fastapi dev" == out.replace("--> ", "")
    runserver(port=8000, dry=True)
    out = capsys.readouterr().out.strip()
    assert "fastapi dev" == out.replace("--> ", "")
    runserver(port=9000, dry=True)
    out = capsys.readouterr().out.strip()
    assert "fastapi dev --port=9000" == out.replace("--> ", "")
    runserver(host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert "fastapi dev --host=0.0.0.0" == out.replace("--> ", "")
    runserver(port=9000, host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert "fastapi dev --port=9000 --host=0.0.0.0" == out.replace("--> ", "")


def test_dev(capsys):
    dev(None, None, dry=True)
    out = capsys.readouterr().out.strip()
    assert "fastapi dev" == out.replace("--> ", "")
    dev(port=8000, host="", dry=True)
    out = capsys.readouterr().out.strip()
    assert "fastapi dev" == out.replace("--> ", "")
    dev(port=9000, host=None, dry=True)
    out = capsys.readouterr().out.strip()
    assert "fastapi dev --port=9000" == out.replace("--> ", "")
    dev(8000, host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert "fastapi dev --host=0.0.0.0" == out.replace("--> ", "")
    dev(port=9000, host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert "fastapi dev --port=9000 --host=0.0.0.0" == out.replace("--> ", "")
