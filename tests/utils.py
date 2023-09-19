import sys
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from pathlib import Path


@contextmanager
def mock_sys_argv(args: list[str]):
    origin = sys.argv[1:]
    sys.argv[1:] = args
    yield
    sys.argv[1:] = origin


@contextmanager
def capture_stdout():
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
