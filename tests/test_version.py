import re
from pathlib import Path

from fast_dev_cli import __version__
from fast_dev_cli.cli import (
    TOML_FILE,
    _parse_version,
    get_current_version,
    read_version_from_file,
    version,
)

from .utils import chdir


def test_version(capsys):
    version()
    assert get_current_version(is_poetry=False) in capsys.readouterr().out
    assert get_current_version(is_poetry=False) == __version__
    assert get_current_version(is_poetry=True) == ""
    assert get_current_version() == __version__


def test_read_version(tmp_path: Path, capsys):
    assert read_version_from_file("fast_dev_cli") == __version__
    toml_text = 'version = "0.1.0"'
    assert read_version_from_file("", toml_text=toml_text) == "0.1.0"
    with chdir(tmp_path):
        tmp_path.joinpath(TOML_FILE).write_text("")
        assert read_version_from_file("") == "0.0.0"
        assert "WARNING" in capsys.readouterr().out
        init_file = tmp_path / "app" / "__init__.py"
        init_file.parent.mkdir()
        init_file.write_text("")
        assert read_version_from_file("") == "0.0.0"
        assert "WARNING" in capsys.readouterr().out
        assert get_current_version() == "0.0.0"


def test_parse_version():
    pattern = re.compile(r"version\s*=")
    line = 'version="0.0.1" # adsfasf version="0.0.2"'
    assert _parse_version(line, pattern) == "0.0.1"
    line = 'version = "0.0.1" # adsfasf version="0.0.2"'
    assert _parse_version(line, pattern) == "0.0.1"
    line = "version = '0.0.1' # adsfasf version=\"0.0.2\""
    assert _parse_version(line, pattern) == "0.0.1"
    line = "version='0.0.1' # adsfasf version=\"0.0.2\""
    assert _parse_version(line, pattern) == "0.0.1"
    line = 'version="0.0.1"'
    assert _parse_version(line, pattern) == "0.0.1"
    pattern = re.compile(r"__version__\s*=")
    line = '__version__ = "0.0.1"'
    assert _parse_version(line, pattern) == "0.0.1"
    line = '__version__ = "0.0.1"  # 0.0.2'
    assert _parse_version(line, pattern) == "0.0.1"
