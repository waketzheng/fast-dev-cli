import shutil
import sys
from collections.abc import Generator
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from pathlib import Path

from asynctor import Shell
from asynctor.compat import chdir

__all__ = (
    "capture_stdout",
    "mock_sys_argv",
    "prepare_poetry_project",
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
    try:
        yield
    finally:
        if path.exists():
            path.unlink()


@contextmanager
def prepare_poetry_project(work_dir: Path) -> Generator[str]:
    py = "{}.{}".format(*sys.version_info)
    poetry = "poetry"
    if shutil.which(poetry) is None:
        poetry = "uvx " + poetry
    project = "foo"
    with chdir(work_dir), _new_poetry_project(py, poetry, project):
        yield poetry


@contextmanager
def _new_poetry_project(py: str, poetry: str, project: str) -> Generator[None]:
    Shell.run_by_subprocess(f"{poetry} new {project} --python=^{py}")
    with chdir(project):
        Shell.run_by_subprocess(f"{poetry} config --local virtualenvs.in-project true")
        Shell.run_by_subprocess(f"{poetry} env use {py}")
        yield
