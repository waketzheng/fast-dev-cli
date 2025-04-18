import os
import subprocess
import sys
from contextlib import AbstractContextManager, contextmanager, redirect_stdout
from io import StringIO
from pathlib import Path


# TODO: use `from contextlib import chdir` instead when drop support for Python3.10
class chdir(AbstractContextManager):  # Copied from source code of Python3.13
    """Non thread-safe context manager to change the current working directory."""

    def __init__(self, path):
        self.path = path
        self._old_cwd = []

    def __enter__(self):
        self._old_cwd.append(os.getcwd())
        os.chdir(self.path)

    def __exit__(self, *excinfo):
        os.chdir(self._old_cwd.pop())


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
