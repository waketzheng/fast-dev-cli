from pathlib import Path

import pytest

from fast_dev_cli.cli import TOML_FILE, EnvError, Sync, run_and_echo, sync

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
        == 'poetry export --without-hashes --extras="all" -o req.txt && poetry run python -m pip install -r req.txt && rm -f req.txt'
    )
    sync(extras="all", save=False, dry=True)
    assert "pip install -r" in capsys.readouterr().out
    mocker.patch(
        "fast_dev_cli.cli.UpgradeDependencies.should_with_dev", return_value=True
    )
    assert (
        Sync("req.txt", "", True, dry=True).gen()
        == "pdm export --without-hashes --with=dev -o req.txt && pdm run python -m pip install -r req.txt"
    )


def test_sync(mocker):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
    test_dir = Path(__file__).parent
    with temp_file(TOML_FILE, TOML_TEXT), chdir(test_dir):
        cmd = Sync("req.txt", "all", save=False, dry=True).gen()
    assert (
        cmd
        == 'poetry export --without-hashes --extras="all" -o req.txt && python -m pip install -r req.txt && rm -f req.txt'
    )
    mocker.patch(
        "fast_dev_cli.cli.UpgradeDependencies.should_with_dev", return_value=True
    )
    assert (
        Sync("req.txt", "", True, dry=True).gen()
        == "pdm export --without-hashes --with=dev -o req.txt && python -m pip install -r req.txt"
    )


UV_TOML_EXAMPLE = """
[project]
name = "examples"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "asynctor>=0.6.6",
]

[tool.uv]
index-url = "https://mirrors.cloud.tencent.com/pypi/simple/"
"""
UV_LOCK_EXAMPLE = """
version = 1
requires-python = ">=3.10"

[[package]]
name = "anyio"
version = "4.6.2.post1"
source = { registry = "https://mirrors.cloud.tencent.com/pypi/simple/" }
dependencies = [
    { name = "exceptiongroup", marker = "python_full_version < '3.11'" },
    { name = "idna" },
    { name = "sniffio" },
    { name = "typing-extensions", marker = "python_full_version < '3.11'" },
]
sdist = { url = "https://mirrors.cloud.tencent.com/pypi/packages/9f/09/45b9b7a6d4e45c6bcb5bf61d19e3ab87df68e0601fa8c5293de3542546cc/anyio-4.6.2.post1.tar.gz", hash = "sha256:4c8bc31ccdb51c7f7bd251f51c609e038d63e34219b44aa86e47576389880b4c" }
wheels = [
    { url = "https://mirrors.cloud.tencent.com/pypi/packages/e4/f5/f2b75d2fc6f1a260f340f0e7c6a060f4dd2961cc16884ed851b0d18da06a/anyio-4.6.2.post1-py3-none-any.whl", hash = "sha256:6d170c36fba3bdd840c73d3868c1e777e33676a69c3a72cf0a0d5d6d8009b61d" },
]

[[package]]
name = "async-timeout"
version = "4.0.3"
source = { registry = "https://mirrors.cloud.tencent.com/pypi/simple/" }
sdist = { url = "https://mirrors.cloud.tencent.com/pypi/packages/87/d6/21b30a550dafea84b1b8eee21b5e23fa16d010ae006011221f33dcd8d7f8/async-timeout-4.0.3.tar.gz", hash = "sha256:4640d96be84d82d02ed59ea2b7105a0f7b33abe8703703cd0ab0bf87c427522f" }
wheels = [
    { url = "https://mirrors.cloud.tencent.com/pypi/packages/a7/fa/e01228c2938de91d47b307831c62ab9e4001e747789d0b05baf779a6488c/async_timeout-4.0.3-py3-none-any.whl", hash = "sha256:7405140ff1230c310e51dc27b3145b9092d659ce68ff733fb0cefe3ee42be028" },
]

[[package]]
name = "asynctor"
version = "0.6.6"
source = { registry = "https://mirrors.cloud.tencent.com/pypi/simple/" }
dependencies = [
    { name = "anyio" },
    { name = "redis" },
]
sdist = { url = "https://mirrors.cloud.tencent.com/pypi/packages/38/d0/452d78491eda3b70bd7b8d401093e5e77999f0232a836b4465e0395223c5/asynctor-0.6.6.tar.gz", hash = "sha256:594c60a38483e399d5a6be513256657989fa2bbf069572074c6b529fa72219ef" }
wheels = [
    { url = "https://mirrors.cloud.tencent.com/pypi/packages/77/01/31143ebf73a22b5e11a1c6dd3f3af53f1d045d9ab0f13a0159b32df71440/asynctor-0.6.6-py3-none-any.whl", hash = "sha256:54785f1cfd32bd9f9bcffe9445ffd02421aab9c3501c134dbd955901606cf1b4" },
]

[[package]]
name = "examples"
version = "0.1.0"
source = { virtual = "." }
dependencies = [
    { name = "asynctor" },
]

[package.metadata]
requires-dist = [{ name = "asynctor", specifier = ">=0.6.6" }]

[[package]]
name = "exceptiongroup"
version = "1.2.2"
source = { registry = "https://mirrors.cloud.tencent.com/pypi/simple/" }
sdist = { url = "https://mirrors.cloud.tencent.com/pypi/packages/09/35/2495c4ac46b980e4ca1f6ad6db102322ef3ad2410b79fdde159a4b0f3b92/exceptiongroup-1.2.2.tar.gz", hash = "sha256:47c2edf7c6738fafb49fd34290706d1a1a2f4d1c6df275526b62cbb4aa5393cc" }
wheels = [
    { url = "https://mirrors.cloud.tencent.com/pypi/packages/02/cc/b7e31358aac6ed1ef2bb790a9746ac2c69bcb3c8588b41616914eb106eaf/exceptiongroup-1.2.2-py3-none-any.whl", hash = "sha256:3111b9d131c238bec2f8f516e123e14ba243563fb135d3fe885990585aa7795b" },
]

[[package]]
name = "idna"
version = "3.10"
source = { registry = "https://mirrors.cloud.tencent.com/pypi/simple/" }
sdist = { url = "https://mirrors.cloud.tencent.com/pypi/packages/f1/70/7703c29685631f5a7590aa73f1f1d3fa9a380e654b86af429e0934a32f7d/idna-3.10.tar.gz", hash = "sha256:12f65c9b470abda6dc35cf8e63cc574b1c52b11df2c86030af0ac09b01b13ea9" }
wheels = [
    { url = "https://mirrors.cloud.tencent.com/pypi/packages/76/c6/c88e154df9c4e1a2a66ccf0005a88dfb2650c1dffb6f5ce603dfbd452ce3/idna-3.10-py3-none-any.whl", hash = "sha256:946d195a0d259cbba61165e88e65941f16e9b36ea6ddb97f00452bae8b1287d3" },
]

[[package]]
name = "redis"
version = "5.1.1"
source = { registry = "https://mirrors.cloud.tencent.com/pypi/simple/" }
dependencies = [
    { name = "async-timeout", marker = "python_full_version < '3.11.3'" },
]
sdist = { url = "https://mirrors.cloud.tencent.com/pypi/packages/e0/58/dcf97c3c09d429c3bb830d6075322256da3dba42df25359bd1c82b442d20/redis-5.1.1.tar.gz", hash = "sha256:f6c997521fedbae53387307c5d0bf784d9acc28d9f1d058abeac566ec4dbed72" }
wheels = [
    { url = "https://mirrors.cloud.tencent.com/pypi/packages/15/f1/feeeaaaac0f589bcbc12c02da357cf635ee383c9128b77230a1e99118885/redis-5.1.1-py3-none-any.whl", hash = "sha256:f8ea06b7482a668c6475ae202ed8d9bcaa409f6e87fb77ed1043d912afd62e24" },
]

[[package]]
name = "sniffio"
version = "1.3.1"
source = { registry = "https://mirrors.cloud.tencent.com/pypi/simple/" }
sdist = { url = "https://mirrors.cloud.tencent.com/pypi/packages/a2/87/a6771e1546d97e7e041b6ae58d80074f81b7d5121207425c964ddf5cfdbd/sniffio-1.3.1.tar.gz", hash = "sha256:f4324edc670a0f49750a81b895f35c3adb843cca46f0530f79fc1babb23789dc" }
wheels = [
    { url = "https://mirrors.cloud.tencent.com/pypi/packages/e9/44/75a9c9421471a6c4805dbf2356f7c181a29c1879239abab1ea2cc8f38b40/sniffio-1.3.1-py3-none-any.whl", hash = "sha256:2f6da418d1f1e0fddd844478f41680e794e6051915791a034ff65e5f100525a2" },
]

[[package]]
name = "typing-extensions"
version = "4.12.2"
source = { registry = "https://mirrors.cloud.tencent.com/pypi/simple/" }
sdist = { url = "https://mirrors.cloud.tencent.com/pypi/packages/df/db/f35a00659bc03fec321ba8bce9420de607a1d37f8342eee1863174c69557/typing_extensions-4.12.2.tar.gz", hash = "sha256:1a7ead55c7e559dd4dee8856e3a88b41225abfe1ce8df57b7c13915fe121ffb8" }
wheels = [
    { url = "https://mirrors.cloud.tencent.com/pypi/packages/26/9f/ad63fc0248c5379346306f8668cda6e2e2e9c95e01216d2b8ffd9ff037d0/typing_extensions-4.12.2-py3-none-any.whl", hash = "sha256:04e5ca0351e0f3f85c6853954072df659d0d13fac324d0072316b67d7794700d" },
]
"""


def test_sync_uv(mocker, tmp_path):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=False)
    with chdir(tmp_path):
        toml = tmp_path / TOML_FILE
        toml.write_text(UV_TOML_EXAMPLE)
        toml.with_name("uv.lock").write_text(UV_LOCK_EXAMPLE)
        assert (
            Sync("req.txt", "", True, dry=True).gen()
            == "uv export --no-hashes --all-extras --frozen -o req.txt && uv run python -m ensurepip && uv run python -m pip install -U pip && uv run python -m pip install -r req.txt"
        )
        run_and_echo("uv run python -m ensurepip")
        assert (
            Sync("req.txt", "", True, dry=True).gen()
            == "uv export --no-hashes --all-extras --frozen -o req.txt && uv run python -m pip install -r req.txt"
        )


def test_sync_no_tool(mocker, tmp_path):
    mocker.patch("fast_dev_cli.cli.is_venv", return_value=False)
    with chdir(tmp_path):
        with pytest.raises(EnvError):
            Sync("req.txt", "", True, dry=True).gen()
        Path("req.txt").write_text("six")
        with pytest.raises(EnvError):
            Sync("req.txt", "", True, dry=True).gen()
        mocker.patch("fast_dev_cli.cli.is_venv", return_value=True)
        assert (
            Sync("req.txt", "", True, dry=True).gen()
            == "python -m pip install -r req.txt"
        )
