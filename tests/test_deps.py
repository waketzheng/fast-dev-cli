from fast_dev_cli.cli import MakeDeps, capture_cmd_output


def test_make_deps_class():
    assert (
        MakeDeps("uv", prod=False).gen()
        == "uv sync --inexact --active --all-extras --all-groups"
    )
    assert MakeDeps("uv", prod=True).gen() == "uv sync --inexact --active"
    assert MakeDeps("pdm", prod=False).gen() == "pdm sync -G :all"
    assert MakeDeps("pdm", prod=True).gen() == "pdm sync --prod"
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
    assert out == "--> pdm sync -G :all"
    out = capture_cmd_output("fast deps --uv --prod --dry")
    assert out == "--> uv sync --inexact --active"
    out = capture_cmd_output("fast deps --uv --dry")
    assert out == "--> uv sync --inexact --active --all-extras --all-groups"
