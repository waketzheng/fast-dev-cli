import shutil
from pathlib import Path

import pytest

from fast_dev_cli.cli import Exit, pypi

ASSERTS_DIR = Path(__file__).parent / "assets"


def test_pypi(tmp_work_dir, capsys):
    uv_qh = ASSERTS_DIR / "uv.lock"
    uv_tx = ASSERTS_DIR / "uv-tx.lock"
    lock_file = Path(uv_qh.name)
    Path("pyproject.toml").touch()
    pypi()
    assert "'uv.lock' not found!" in capsys.readouterr().out
    shutil.copy(uv_qh, ".")
    text = uv_qh.read_text("utf-8")
    with pytest.raises(Exit):
        pypi()
    new_text = lock_file.read_text("utf-8")
    assert new_text != text
    assert "tsinghua" in text and "pypi.org" not in text
    assert "tsinghua" not in new_text and "pypi.org" in new_text
    lock_file.write_text(text, encoding="utf-8")
    pypi(quiet=True)
    assert new_text == lock_file.read_text("utf-8")
    pypi()
    assert new_text == lock_file.read_text("utf-8")

    shutil.copy(uv_tx, lock_file)
    text = lock_file.read_text("utf-8")
    with pytest.raises(Exit):
        pypi()
    new_text = lock_file.read_text("utf-8")
    assert new_text != text
    assert "tencent" in text and "pypi.org" not in text
    assert "tencent" not in new_text and "pypi.org" in new_text
    lock_file.write_text(text, encoding="utf-8")
    pypi(quiet=True)
    assert new_text == lock_file.read_text("utf-8")
    pypi()
    assert new_text == lock_file.read_text("utf-8")

    lock_file = Path(uv_tx.name)
    shutil.copy(uv_tx, ".")
    text = lock_file.read_text("utf-8")
    with pytest.raises(Exit):
        pypi(uv_tx.name)
    new_text = lock_file.read_text("utf-8")
    shutil.copy(uv_tx, ".")
    pypi(uv_tx.name, quiet=True)
    assert new_text == lock_file.read_text("utf-8")
    pypi(uv_tx.name)
    assert new_text == lock_file.read_text("utf-8")


def test_pypi_slim(tmp_work_dir, capsys):
    origin_lock = ASSERTS_DIR / "uv-upload-time.lock"
    lock_file = Path("uv.lock")
    Path("pyproject.toml").touch()
    pypi()
    assert "'uv.lock' not found!" in capsys.readouterr().out
    shutil.copy(origin_lock, lock_file)
    text = origin_lock.read_text("utf-8")
    with pytest.raises(Exit):
        pypi()
    new_text = lock_file.read_text("utf-8")
    assert new_text != text
    assert "aliyun" in text and "pypi.org" not in text
    assert "aliyun" not in new_text and "pypi.org" in new_text
    assert "upload-time" in new_text
    pypi(slim=True, verbose=True)
    assert "upload-time" in new_text
    assert "no need to change" in capsys.readouterr().out
    shutil.copy(origin_lock, lock_file)
    pypi(slim=True, quiet=True)
    new_text = lock_file.read_text("utf-8")
    assert "pypi.org" in new_text
    assert "upload-time" not in new_text
