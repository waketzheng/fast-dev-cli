import shlex
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


@contextmanager
def prepare_poetry_project(tmp_path: Path):
    with chdir(tmp_path):
        project = "foo"
        subprocess.run(["poetry", "new", project])
        with chdir(tmp_path / project):
            yield


def get_cmd_output(cmd: str) -> str:
    r = subprocess.run(
        shlex.split(cmd), capture_output=True, text=True, encoding="utf-8"
    )
    return r.stdout.strip()
