import os

from fast_dev_cli.cli import TOML_FILE, run_and_echo, upload

from .utils import chdir


def test_upload(capsys):
    upload(dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "pdm publish"


def test_upload_poetry(tmp_path, capsys):
    with chdir(tmp_path):
        run_and_echo("poetry new foo", verbose=False)
    with chdir(tmp_path / "foo"):
        upload(dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "poetry publish --build"


def test_upload_uv(tmp_path, capsys):
    project_dir = tmp_path / "uv_proj"
    project_dir.mkdir()
    toml_file = project_dir / TOML_FILE
    with chdir(project_dir):
        run_and_echo("uv init", verbose=False)
        if (s := "[tool.uv]") not in (text := toml_file.read_text()):
            toml_file.write_text(text + os.linesep + s)
        upload(dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "uv build && uv publish"


def test_upload_other(tmp_path, capsys):
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    with chdir(project_dir):
        run_and_echo("uv init", verbose=False)
        upload(dry=True)
    out = capsys.readouterr().out.strip()
    assert out.replace("--> ", "") == "python -m build && twine upload"
