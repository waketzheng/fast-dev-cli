#!/usr/bin/env python
"""
Install deps by `pdm install -G :all --frozen`
if value of `pdm config use_uv` is True,
otherwise by the following shells:

    pdm run python -m ensurepip
    pdm run python -m pip install --upgrade pip
    pdm run python -m pip install --group dev -e .

Usage::
    pdm run python scripts/deps.py
"""

from __future__ import annotations

import os
import platform
import shlex
import subprocess
import sys
from pathlib import Path

__version__ = "0.1.3"
__updated_at__ = "2025.07.21"
SHELL = """
pdm run python -m ensurepip
pdm run python -m pip install --upgrade pip
pdm run python -m pip install --group dev -e .
"""


def run_and_echo(
    cmd: str,
    env: dict[str, str] | None = None,
    dry: bool = False,
    verbose: bool = True,
    **kw,
) -> int:
    if verbose:
        print("-->", cmd)
    if dry:
        return 0
    if env is not None:
        env = dict(os.environ, **env)
    return subprocess.run(shlex.split(cmd), env=env, **kw).returncode


def capture_output(cmd: str) -> str:
    r = subprocess.run(
        shlex.split(cmd), capture_output=True, text=True, encoding="utf-8"
    )
    return r.stdout.strip()


def is_using_uv() -> bool:
    return capture_output("pdm config use_uv").lower() == "true"


def pop_if_contains(args: list[str], flag: str) -> bool:
    try:
        index = args.index(flag)
    except ValueError:
        return False
    else:
        args.pop(index)
        return True


def prefer_pdm(args: list[str]) -> bool:
    if pop_if_contains(args, "--pip"):
        return False
    return platform.system() != "Windows" or is_using_uv()


def not_distribution() -> bool:
    toml = Path(__file__).parent / "pyproject.toml"
    if not toml.exists():
        toml = toml.parent.parent / toml.name
        if not toml.exists():
            return False
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        try:
            import tomli as tomllib
        except ImportError:
            return False
    doc = tomllib.loads(toml.read_text("utf8"))
    try:
        return not doc["tool"]["pdm"]["distribution"]
    except KeyError:
        ...
    return False


def run_shell(command: str, args: list[str], dry: bool) -> int | None:
    if args:
        command += " " + " ".join(i if i.startswith("-") else repr(i) for i in args)
    if run_and_echo(command, dry=dry) == 0:
        return None
    return 1


def pip_available() -> bool:
    rc = run_and_echo(
        "pdm run python -m pip --version", capture_output=True, verbose=False
    )
    return rc == 0


def main() -> int | None:
    args = sys.argv[1:]
    if len(args) == 1:
        a1 = args[0]
        if a1 == "-h" or "--help" in args:
            print(__doc__)
            return None
        elif a1 in ("-v", "--version"):
            print(__version__)
            return None
    dry = pop_if_contains(args, "--dry") or pop_if_contains(args, "--dry-run")
    if pop_if_contains(args, "--uv"):
        if os.path.exists("uv.lock"):
            return run_shell("uv sync --all-extras --all-groups", args, dry)
        command = (
            "uv install --all-extras -r pyproject.toml --group dev --no-verify-hashes"
        )
        return run_shell(command, args, dry)
    if prefer_pdm(args):
        command = "pdm install --frozen -G :all"
        return run_shell(command, args, dry)
    shell = SHELL.strip()
    if pop_if_contains(args, "--no-dev"):
        shell = shell.replace(" --group dev", "")
    if args:
        extras = " ".join(i if i.startswith("-") else repr(i) for i in args)
        if extras.startswith("-"):
            shell += " " + extras
        else:
            shell += extras  # e.g.: '[xls,fastapi]'
    elif not_distribution():
        shell = shell.replace(" -e .", "")
    cmds = shell.splitlines()
    if pip_available():  # If pip exists, skip installing it by ensurepip
        cmds = cmds[1:]
    for cmd in cmds:
        if run_and_echo(cmd, dry=dry) != 0:
            return 1
    if not dry:
        print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
