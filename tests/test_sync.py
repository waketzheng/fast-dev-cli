from pathlib import Path

from fast_dev_cli.cli import TOML_FILE, Sync, sync

from .utils import chdir, temp_file

TOML_TEXT = """
[tool.poetry]
name = "foo"
version = "0.1.0"
description = ""
authors = []
readme = ""

[tool.poetry.dependencies]
python = "^3.11"
click = ">=7.1.1"
anyio = {version = "^4.0", optional = true}

[tool.poetry.extras]
all = ["anyio"]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""


def test_sync_not_in_venv(mocker, capsys):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=False)
    test_dir = Path(__file__).parent
    with temp_file(TOML_FILE, TOML_TEXT), chdir(test_dir):
        cmd = Sync("req.txt", "all", save=False, dry=True).gen()
    assert (
        cmd
        == "poetry export --extras='all' --without-hashes -o req.txt && poetry run pip install -r req.txt && rm -f req.txt"
    )
    sync(extras="all", save=False, dry=True)
    assert "pip install -r" in capsys.readouterr().out
    mocker.patch(
        "fast_dev_cli.cli.UpgradeDependencies.should_with_dev", return_value=True
    )
    assert (
        Sync("req.txt", "", True, dry=True).gen()
        == "poetry export --with=dev --without-hashes -o req.txt && poetry run pip install -r req.txt"
    )


def test_sync(mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    test_dir = Path(__file__).parent
    with temp_file(TOML_FILE, TOML_TEXT), chdir(test_dir):
        cmd = Sync("req.txt", "all", save=False, dry=True).gen()
    assert (
        cmd
        == "poetry export --extras='all' --without-hashes -o req.txt && pip install -r req.txt && rm -f req.txt"
    )
    mocker.patch(
        "fast_dev_cli.cli.UpgradeDependencies.should_with_dev", return_value=True
    )
    assert (
        Sync("req.txt", "", True, dry=True).gen()
        == "poetry export --with=dev --without-hashes -o req.txt && pip install -r req.txt"
    )
