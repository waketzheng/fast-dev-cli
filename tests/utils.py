import shlex
import shutil
import subprocess
import sys
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from pathlib import Path

from asynctor.compat import chdir

__all__ = (
    "chdir",
    "mock_sys_argv",
    "capture_stdout",
    "temp_file",
)


@contextmanager
def mock_sys_argv(args: list[str]):
    origin = sys.argv[1:]
    sys.argv[1:] = args
    yield
    sys.argv[1:] = origin


@contextmanager
def capture_stdout():
    """Redirect sys.stdout to a new StringIO

    Example::
    ```py
        with capture_stdout() as stream:
            GitTag(message="", dry=True).run()
        assert "git tag -a" in stream.getvalue()
    ```
    """
    stream = StringIO()
    with redirect_stdout(stream):
        yield stream


@contextmanager
def temp_file(name: str, text=""):
    path = Path(__file__).parent / name
    if text:
        path.write_text(text)
    else:
        path.touch()
    yield
    if path.exists():
        path.unlink()


def _run_shell(cmd: str, **kw) -> subprocess.CompletedProcess[str]:
    if (shell := kw.get("shell")) is None and ("|" in cmd or ">" in cmd):
        kw["shell"] = shell = True
    command = cmd if shell else shlex.split(cmd)
    return subprocess.run(command, **kw)  # nosec


@contextmanager
def prepare_poetry_project(tmp_path: Path):
    py = "{}.{}".format(*sys.version_info)
    poetry = "poetry"
    if shutil.which(poetry) is None:
        poetry = "uvx " + poetry
    with chdir(tmp_path):
        project = "foo"
        _run_shell(f"{poetry} new {project} --python=^{py}")  # nosec
        with chdir(tmp_path / project):
            _run_shell(f"{poetry} config --local virtualenvs.in-project true")  # nosec
            _run_shell(f"{poetry} env use {py}")  # nosec
            yield


def get_cmd_output(cmd: str) -> str:
    r = _run_shell(cmd, capture_output=True, text=True, encoding="utf-8")
    return r.stdout.strip()
