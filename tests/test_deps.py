import re
import shutil
from pathlib import Path

from tomli_w import dumps

from fast_dev_cli.cli import MakeDeps, capture_cmd_output, run_and_echo, tomllib

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def test_make_deps_class():
    class PipDepsWithoutEnsure(MakeDeps):
        def should_ensure_pip(self) -> bool:
            return False

    assert (
        MakeDeps("uv", prod=False).gen()
        == "uv sync --reinstall-package=fast-dev-cli --all-extras --all-groups"
    )
    assert (
        MakeDeps("uv", prod=False, inexact=True, active=True).gen()
        == "uv sync --reinstall-package=fast-dev-cli --inexact --active --all-extras --all-groups"
    )
    assert (
        MakeDeps("uv", prod=False, inexact=True).gen()
        == "uv sync --reinstall-package=fast-dev-cli --inexact --all-extras --all-groups"
    )
    assert (
        MakeDeps("uv", prod=True).gen()
        == "uv sync --reinstall-package=fast-dev-cli --no-dev"
    )
    assert (
        MakeDeps("uv", prod=True, inexact=True).gen()
        == "uv sync --reinstall-package=fast-dev-cli --inexact --no-dev"
    )
    assert MakeDeps("pdm", prod=False).gen() == "pdm install --frozen -G :all"
    assert MakeDeps("pdm", prod=True).gen() == "pdm install --frozen --prod"
    assert (
        MakeDeps("poetry", prod=False).gen()
        == "poetry install --all-extras --all-groups"
    )
    assert MakeDeps("poetry", prod=True).gen() == "poetry install --only=main"
    assert (
        MakeDeps("pip", prod=False).gen()
        == "python -m ensurepip && python -m pip install --upgrade pip && python -m pip install -e . --group dev"
    )
    assert (
        MakeDeps("pip", prod=True).gen()
        == "python -m ensurepip && python -m pip install --upgrade pip && python -m pip install -e ."
    )
    assert (
        PipDepsWithoutEnsure("pip", prod=False).gen()
        == "python -m pip install --upgrade pip && python -m pip install -e . --group dev"
    )


def test_fast_deps():
    out = capture_cmd_output("fast deps --pdm --dry")
    assert out == "--> pdm install --frozen -G :all"
    out = capture_cmd_output("fast deps --uv --prod --dry")
    assert out == "--> uv sync --reinstall-package=fast-dev-cli --no-dev"
    out = capture_cmd_output("fast deps --uv --prod --dry --inexact --active")
    assert (
        out
        == "--> uv sync --reinstall-package=fast-dev-cli --inexact --active --no-dev"
    )
    out = capture_cmd_output("fast deps --uv --prod --dry --no-active")
    assert out == "--> uv sync --reinstall-package=fast-dev-cli --no-dev"
    out = capture_cmd_output("fast deps --uv --prod --dry --no-inexact")
    assert out == "--> uv sync --reinstall-package=fast-dev-cli --no-dev"
    out = capture_cmd_output("fast deps --uv --prod --dry --no-active --no-inexact")
    assert out == "--> uv sync --reinstall-package=fast-dev-cli --no-dev"
    out = capture_cmd_output("fast deps --uv --dry")
    assert (
        out == "--> uv sync --reinstall-package=fast-dev-cli --all-extras --all-groups"
    )
    out = capture_cmd_output("fast deps --uv --dry --frozen")
    assert (
        out
        == "--> uv sync --reinstall-package=fast-dev-cli --all-extras --all-groups --frozen"
    )
    out = capture_cmd_output("fast deps --uv --dry --frozen-lockfile")
    assert (
        out
        == "--> uv sync --reinstall-package=fast-dev-cli --all-extras --all-groups --frozen"
    )
    out = capture_cmd_output("fast deps --uv --dry --no-lock")
    assert (
        out
        == "--> uv sync --reinstall-package=fast-dev-cli --all-extras --all-groups --frozen"
    )
    out = capture_cmd_output("fast deps --uv --dry --inexact")
    assert (
        out
        == "--> uv sync --reinstall-package=fast-dev-cli --inexact --all-extras --all-groups"
    )
    out = capture_cmd_output("fast deps --uv --dry --active")
    assert (
        out
        == "--> uv sync --reinstall-package=fast-dev-cli --active --all-extras --all-groups"
    )
    out = capture_cmd_output("fast deps --uv --dry --active --inexact")
    assert (
        out
        == "--> uv sync --reinstall-package=fast-dev-cli --inexact --active --all-extras --all-groups"
    )


def test_reinstall_package(tmp_work_dir):
    out = capture_cmd_output("fast deps --uv --dry")
    assert out == "--> uv sync --all-extras --all-groups"
    toml_file = Path("pyproject.toml")
    shutil.copy(Path(__file__).parent.parent.joinpath(toml_file.name), toml_file)
    text = toml_file.read_text(encoding="utf-8")
    doc = tomllib.loads(text)
    doc["tool"]["pdm"]["distribution"] = False
    toml_file.write_text(dumps(doc), encoding="utf-8")
    out = capture_cmd_output("fast deps --uv --dry")
    assert out == "--> uv sync --all-extras --all-groups"
    doc["tool"]["pdm"]["distribution"] = True
    doc["tool"]["uv"] = {"package": False}
    toml_file.write_text(dumps(doc), encoding="utf-8")
    out = capture_cmd_output("fast deps --uv --dry")
    assert out == "--> uv sync --all-extras --all-groups"
    doc["tool"]["uv"]["package"] = True
    doc["project"]["name"] += "2"
    toml_file.write_text(dumps(doc), encoding="utf-8")
    out = capture_cmd_output("fast deps --uv --dry")
    assert (
        out == "--> uv sync --reinstall-package=fast-dev-cli2 --all-extras --all-groups"
    )
    doc["build-system"]["build-backend"] = "poetry"
    doc["tool"]["poetry"] = {"package-mode": False}
    toml_file.write_text(dumps(doc), encoding="utf-8")
    out = capture_cmd_output("fast deps --uv --dry")
    assert (
        out == "--> uv sync --reinstall-package=fast-dev-cli2 --all-extras --all-groups"
    )
    doc["tool"].pop("uv")
    toml_file.write_text(dumps(doc), encoding="utf-8")
    out = capture_cmd_output("fast deps --uv --dry")
    assert out == "--> uv sync --all-extras --all-groups"
    doc["build-system"]["build-backend"] = "hatchling.build"
    toml_file.write_text(dumps(doc), encoding="utf-8")
    out = capture_cmd_output("fast deps --uv --dry")
    assert (
        out == "--> uv sync --reinstall-package=fast-dev-cli2 --all-extras --all-groups"
    )


def test_fast_deps_mutually_exclusive_options():
    cmd = "fast deps --uv --pdm --dry"
    assert run_and_echo(cmd, verbose=False) == 2
    out = strip_ansi(capture_cmd_output(cmd))
    assert "Invalid value for '--uv' / '--pdm' / '--pip' / '--poetry'" in out
    assert "can only choose" in out


def test_smart_fast_deps(tmp_work_dir, monkeypatch):
    toml_file = tmp_work_dir.joinpath("pyproject.toml")
    if toml_file.exists():
        toml_file.unlink()
    tmp_work_dir.joinpath("uv.lock").touch()
    out = capture_cmd_output("fast deps --dry")
    assert (
        out
        == "--> python -m ensurepip && python -m pip install --upgrade pip && python -m pip install -e . --group dev"
    )
    toml_file.touch()
    out = capture_cmd_output("fast deps --dry")
    assert out == "--> uv sync --all-extras --all-groups"
    out = capture_cmd_output("fast deps --dry --inexact --active")
    assert out == "--> uv sync --inexact --active --all-extras --all-groups"
    pdm_lock = tmp_work_dir.joinpath("pdm.lock")
    pdm_lock.touch()
    out = capture_cmd_output("fast deps --dry")
    assert out == "--> uv sync --all-extras --all-groups"
    out = capture_cmd_output("fast deps --dry --inexact --active")
    assert out == "--> uv sync --inexact --active --all-extras --all-groups"
    toml_file.write_text("[tool.pdm]\ndistribution=false")
    out = capture_cmd_output("fast deps --dry")
    assert out == "--> uv sync --all-extras --all-groups"
    out = capture_cmd_output("fast deps --dry --inexact --active")
    assert out == "--> uv sync --inexact --active --all-extras --all-groups"
    monkeypatch.setenv("FASTDEVCLI_SKIP_UV", "1")
    out = capture_cmd_output("fast deps --dry")
    assert out == "--> pdm install --frozen -G :all"
    pdm_lock.unlink()
    out = capture_cmd_output("fast deps --dry")
    assert out == "--> pdm install --frozen -G :all"
