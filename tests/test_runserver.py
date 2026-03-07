from __future__ import annotations

import functools

import fast_dev_cli
from fast_dev_cli.cli import dev, main, run_and_echo, runserver


def test_runserver(capsys):
    runserver(dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev"
    runserver(port=8000, dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev"
    runserver(port=9000, dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev --port=9000"
    runserver(host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev --host=0.0.0.0"
    runserver(port=9000, host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev --host=0.0.0.0 --port=9000"
    runserver("9000", host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev --host=0.0.0.0 --port=9000"
    runserver("app.py", host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev app.py --host=0.0.0.0"


def test_runserver_no_pdm(capsys, mocker):
    mocker.patch("shutil.which", return_value=None)
    runserver(dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "fastapi dev"
    runserver(file_or_port=":8000", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "fastapi dev --port=8000"
    runserver(file_or_port="0:9000", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "fastapi dev --host=0.0.0.0 --port=9000"
    runserver(file_or_port="0.0.0.0:8000", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "fastapi dev --host=0.0.0.0 --port=8000"
    runserver(port=9000, host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "fastapi dev --host=0.0.0.0 --port=9000"
    runserver("9000", host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "fastapi dev --host=0.0.0.0 --port=9000"
    runserver("app.py", uvicorn=True, host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "uvicorn app:app --host=0.0.0.0"
    runserver(
        "tests/test_runserver.py", uvicorn=True, port=9999, host="0.0.0.0", dry=True
    )
    out = capsys.readouterr().out.strip()
    assert (
        out.replace("--> ", "")
        == "uvicorn tests.test_runserver:app --host=0.0.0.0 --port=9999"
    )


def test_dev(capsys):
    dev(None, None, dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev"
    dev(port=8000, host="", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev"
    dev(port=9000, host=None, dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev --port=9000"
    dev(8000, host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev --host=0.0.0.0"
    dev(port=9000, host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev --host=0.0.0.0 --port=9000"
    dev(8001, host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev --host=0.0.0.0 --port=8001"
    dev(None, file="8001", host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev --host=0.0.0.0 --port=8001"
    dev(None, file="main.py", host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm run fastapi dev main.py --host=0.0.0.0"
    dev(8001, file="main.py", host="0.0.0.0", dry=True)
    out = capsys.readouterr().out.strip()
    assert (
        out.replace("--> ", "")
        == "pdm run fastapi dev main.py --host=0.0.0.0 --port=8001"
    )


def test_fast_dev(tmp_path):
    file = tmp_path / "a.txt"
    read_text = functools.partial(file.read_text, encoding="utf-8")
    run_and_echo(f"fast dev 9000 --dry > {file}", verbose=False)
    assert "fastapi dev --port=9000" in read_text()
    run_and_echo(f"fast dev main.py --dry > {file}", verbose=False)
    assert "fastapi dev main.py" in read_text()
    run_and_echo(f"fast dev main.py --port=9000 --dry > {file}", verbose=False)
    assert "fastapi dev main.py --port=9000" in read_text()
    run_and_echo(
        f"fast dev main.py --host=0.0.0.0 --port=9000 --dry > {file}", verbose=False
    )
    assert "fastapi dev main.py --host=0.0.0.0 --port=9000" in read_text()
    run_and_echo(f"fast dev 9000 --host=0.0.0.0 --dry > {file}", verbose=False)
    assert "fastapi dev --host=0.0.0.0 --port=9000" in read_text()


def test_run_by_module(tmp_path):
    out = tmp_path / "b.txt"
    fast = "python -m fast_dev_cli"
    run_and_echo(f"{fast} dev 9000 --dry > {out}", verbose=False)
    assert "fastapi dev --port=9000" in out.read_text()
    run_and_echo(f"{fast} dev main.py --dry > {out}", verbose=False)
    assert "fastapi dev main.py" in out.read_text()
    run_and_echo(f"{fast} dev main.py --port=9000 --dry > {out}", verbose=False)
    assert "fastapi dev main.py --port=9000" in out.read_text()
    run_and_echo(
        f"{fast} dev main.py --host=0.0.0.0 --port=9000 --dry > {out}", verbose=False
    )
    assert "fastapi dev main.py --host=0.0.0.0 --port=9000" in out.read_text()
    run_and_echo(f"{fast} dev 9000 --host=0.0.0.0 --dry > {out}", verbose=False)
    assert "fastapi dev --host=0.0.0.0 --port=9000" in out.read_text()


def test_main(mocker):
    mocker.patch("fast_dev_cli.cli.cli")
    main()
    fast_dev_cli.cli.cli.assert_called_once()  # type:ignore[attr-defined]
