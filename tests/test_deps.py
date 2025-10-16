from fast_dev_cli.cli import MakeDeps, capture_cmd_output


def test_make_deps_class():
    assert (
        MakeDeps("uv", prod=False).gen()
        == "uv sync --inexact --active --all-extras --all-groups"
    )
    assert (
        MakeDeps("uv", prod=False, active=False).gen()
        == "uv sync --inexact --all-extras --all-groups"
    )
    assert MakeDeps("uv", prod=True).gen() == "uv sync --inexact --active"
    assert MakeDeps("uv", prod=True, active=False).gen() == "uv sync --inexact"
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


def test_fast_deps():
    out = capture_cmd_output("fast deps --dry")
    assert out == "--> pdm install --frozen -G :all"
    out = capture_cmd_output("fast deps --uv --prod --dry")
    assert out == "--> uv sync --inexact --active"
    out = capture_cmd_output("fast deps --uv --prod --dry --no-active")
    assert out == "--> uv sync --inexact"
    out = capture_cmd_output("fast deps --uv --prod --dry --no-inexact")
    assert out == "--> uv sync --active"
    out = capture_cmd_output("fast deps --uv --prod --dry --no-active --no-inexact")
    assert out == "--> uv sync"
    out = capture_cmd_output("fast deps --uv --dry")
    assert out == "--> uv sync --inexact --active --all-extras --all-groups"
    out = capture_cmd_output("fast deps --uv --dry --no-active")
    assert out == "--> uv sync --inexact --all-extras --all-groups"
    out = capture_cmd_output("fast deps --uv --dry --no-inexact")
    assert out == "--> uv sync --active --all-extras --all-groups"
    out = capture_cmd_output("fast deps --uv --dry --no-active --no-inexact")
    assert out == "--> uv sync --all-extras --all-groups"


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
    assert out == "--> uv sync --inexact --active --all-extras --all-groups"
    pdm_lock = tmp_work_dir.joinpath("pdm.lock")
    pdm_lock.touch()
    out = capture_cmd_output("fast deps --dry")
    assert out == "--> uv sync --inexact --active --all-extras --all-groups"
    toml_file.write_text("[tool.pdm]\ndistribution=false")
    out = capture_cmd_output("fast deps --dry")
    assert out == "--> uv sync --inexact --active --all-extras --all-groups"
    monkeypatch.setenv("FASTDEVCLI_SKIP_UV", "1")
    out = capture_cmd_output("fast deps --dry")
    assert out == "--> pdm install --frozen -G :all"
    pdm_lock.unlink()
    out = capture_cmd_output("fast deps --dry")
    assert out == "--> pdm install --frozen -G :all"
