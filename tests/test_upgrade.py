from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from fast_dev_cli.cli import (
    TOML_FILE,
    UpgradeDependencies,
    run_and_echo,
    upgrade,
)

from .utils import chdir, is_newer_version_python


def test_parse_value():
    s = 'typer = {extras = ["all"], version = "^0.9.0", optional = true}'
    assert UpgradeDependencies.parse_value(s, "version") == "^0.9.0"
    assert UpgradeDependencies.parse_value(s, "extras") == "all"
    assert UpgradeDependencies.parse_value(s, "optional") == "true"
    s = 'tortoise-orm = {extras = ["asyncpg","aiomysql"], version = "*"}'
    assert UpgradeDependencies.parse_value(s, "extras") == "asyncpg,aiomysql"


def test_no_need_upgrade():
    s = 'typer = "^0.9.0"'
    assert not UpgradeDependencies.no_need_upgrade(s.split("=", 1)[-1].strip(' "'), s)
    s = 'typer = {extras = ["all"], version = "^0.9.0", optional = true}'
    assert not UpgradeDependencies.no_need_upgrade(s.split("=", 1)[-1].strip(' "'), s)

    s = 'typer = "*"'
    assert UpgradeDependencies.no_need_upgrade(s.split("=", 1)[-1].strip(' "'), s)
    s = 'typer = {extras = ["all"], version = "*", optional = true}'
    assert UpgradeDependencies.no_need_upgrade(s.split("=", 1)[-1].strip(' "'), s)
    s = 'typer = {extras = ["all"], version = ">=0.9", optional = true}'
    assert UpgradeDependencies.no_need_upgrade(s.split("=", 1)[-1].strip(' "'), s)
    s = 'typer = {url = "https://github.com/tiangolo/typer"}'
    assert UpgradeDependencies.no_need_upgrade(s.split("=", 1)[-1].strip(' "'), s)


def test_build_args():
    segment = """bumpversion = "*"
fastapi = {extras = ["all"], version = "*"}
ipython = "^8.15.0"
coveralls = "^3.3.1"
pytest-mock = "^3.11.1"
tortoise-orm = {extras = ["asyncpg"], version = "^0.20"}
gunicorn = {version = "^21.2.0", platform = "linux"}
orjson = {version = "^3.9.7", source = "jumping"}
anyio = {version = ">=3.7.1", optional = true}
typer = {extras = ["all"], version = "^0.9.0", optional = true}
uvicorn = {version = "^0.23.2", platform = "linux", optional = true}
    """
    assert UpgradeDependencies.build_args(segment.splitlines()) == (
        [
            '"ipython@latest"',
            '"coveralls@latest"',
            '"pytest-mock@latest"',
            '"tortoise-orm[asyncpg]@latest"',
        ],
        {
            "--platform=linux": ['"gunicorn@latest"'],
            "--source=jumping": ['"orjson@latest"'],
            "--optional": ['"typer[all]@latest"'],
            "--platform=linux --optional": ['"uvicorn@latest"'],
        },
    )
    # After module reloaded by test_click, pytest failed to catch ParseError
    # with pytest.raises(ParseError):
    #     UpgradeDependencies.build_args(["[tool.isort]"])
    try:
        UpgradeDependencies.build_args(["[tool.isort]"])
    except Exception as e:
        assert type(e).__name__ == "ParseError"
    assert UpgradeDependencies.build_args(['python = "^3.8"']) == ([], {})


def test_dev_flag(tmp_path: Path):
    assert UpgradeDependencies.should_with_dev() is False
    with chdir(tmp_path):
        project = tmp_path / "project"
        run_and_echo(f"poetry new {project.name}")
        with chdir(project):
            if not is_newer_version_python:
                p = Path("pyproject.toml")
                content = p.read_text()
                s = 'python = "^3.11"'
                ss = s.replace("3.11", "3.10")
                p.write_text(content.replace(s, ss))
            assert not UpgradeDependencies.should_with_dev()
            run_and_echo("poetry add pytest")
            assert not UpgradeDependencies.should_with_dev()
            run_and_echo("poetry add --group=dev typer")
            assert UpgradeDependencies.should_with_dev()
            text = project.joinpath(TOML_FILE).read_text()
            DevFlag = UpgradeDependencies.DevFlag
            if DevFlag.new in text:
                new_text = text.replace(DevFlag.new, DevFlag.old)
            else:
                new_text = text.replace(DevFlag.old, DevFlag.new)
            project.joinpath(TOML_FILE).write_text(new_text)
            assert UpgradeDependencies.should_with_dev()


def test_parse_item():
    segment = """
[tool.poetry.dependencies]
bumpversion = "*"
fastapi = {extras = ["all"], version = "*"}

[tool.isort]
    """.strip()
    assert UpgradeDependencies.parse_item(segment) == [
        'bumpversion = "*"',
        'fastapi = {extras = ["all"], version = "*"}',
    ]


def test_get_args_hard(tmp_poetry_project):
    assert UpgradeDependencies.get_args() == (
        [],
        [
            '"typer@latest"',
            '"ruff@latest"',
            '"mypy@latest"',
            '"pytest@latest"',
            '"ipython@latest"',
            '"bumpversion@latest"',
            '"pytest-mock@latest"',
            '"type-extensions@latest"',
            '"strenum@latest"',
        ],
        [
            [
                "--optional",
                '"ruff@latest"',
                '"mypy@latest"',
                '"bumpversion@latest"',
                '"pytest@latest"',
                '"typer@latest"',
            ]
        ],
        "--group dev",
    )


def test_get_dev_dependencies(tmp_path: Path):
    assert UpgradeDependencies.manage_by_poetry() is False
    try:
        UpgradeDependencies.get_args()
    except Exception as e:
        assert type(e).__name__ == "EnvError"
    dev_text = """
[tool.poetry.dev-dependencies]
anyio = "^4.0"
    """
    with chdir(tmp_path):
        project = tmp_path / "project"
        run_and_echo(f"poetry new {project.name}")
        with chdir(project):
            with project.joinpath(TOML_FILE).open("a") as f:
                f.write(dev_text)
            assert UpgradeDependencies.get_args() == (
                [],
                ['"anyio@latest"'],
                [],
                "--dev",
            )


def test_get_args(tmp_path: Path):
    segment = """
[tool.poetry.dependencies]
anyio = "^4.0"
    """
    assert UpgradeDependencies.get_args(segment) == (
        ['"anyio@latest"'],
        [],
        [],
        "--dev",
    )
    segment = """
[tool.poetry.dependencies]
anyio = "^4.0"

[tool.poetry.dev-dependencies]
pytest = {version = "^4.0", platform = "linux"}
    """
    assert UpgradeDependencies.get_args(segment) == (
        ['"anyio@latest"'],
        [],
        [["--platform=linux", '"pytest@latest"', "--dev"]],
        "--dev",
    )


def test_gen_cmd(tmp_poetry_project):
    expected = 'poetry add --group dev "typer@latest" "ruff@latest" "mypy@latest" "pytest@latest" "ipython@latest" "bumpversion@latest" "pytest-mock@latest" "type-extensions@latest" "strenum@latest" && poetry add --optional "ruff@latest" "mypy@latest" "bumpversion@latest" "pytest@latest" "typer@latest"'
    assert UpgradeDependencies.gen_cmd() == expected
    assert UpgradeDependencies().gen() == expected + " && poetry lock && poetry update"
    stream = StringIO()
    with redirect_stdout(stream):
        upgrade(dry=True)
    assert expected in stream.getvalue()
    args: tuple = (
        ['"anyio@latest"'],
        [],
        [["--platform=linux", '"pytest@latest"', "--dev"]],
        "--dev",
    )
    assert (
        UpgradeDependencies.to_cmd(*args)
        == 'poetry add "anyio@latest" && poetry add --platform=linux "pytest@latest" --dev'
    )
    assert UpgradeDependencies.manage_by_poetry() is True


def test_args_to_cmd():
    args: tuple = (
        [],
        ['"anyio@latest"'],
        [["--platform=linux", '"pytest@latest"', "--dev"]],
        "--dev",
    )
    assert (
        UpgradeDependencies.to_cmd(*args)
        == 'poetry add --dev "anyio@latest" && poetry add --platform=linux "pytest@latest" --dev'
    )
    args = (
        ['"anyio@latest"'],
        [],
        [],
        "--dev",
    )
    assert UpgradeDependencies.to_cmd(*args) == 'poetry add "anyio@latest"'
    args = (
        ['"anyio@latest"'],
        ['"ipython@latest"'],
        [],
        "--dev",
    )
    assert (
        UpgradeDependencies.to_cmd(*args)
        == 'poetry add "anyio@latest" && poetry add --dev "ipython@latest"'
    )


def test_get_dir(mocker, tmp_path):
    me = Path(__file__)
    parent = me.parent
    root = parent.parent
    assert (
        UpgradeDependencies.get_work_dir() == UpgradeDependencies.get_root_dir() == root
    )
    with chdir(parent):
        mocker.patch.object(
            UpgradeDependencies, "python_exec_dir", return_value=tmp_path
        )
        assert UpgradeDependencies.get_root_dir() == parent
        mocker.patch.object(UpgradeDependencies, "python_exec_dir", return_value=me)
        assert UpgradeDependencies.get_root_dir() == root


def test_parse_complex_segment():
    segment = """
[tool.poetry.dependencies]
torch = [
    {version="*",platform="linux"},
    {version="^1.2.0",platform=""},
    {version=">=1.2.0",platform=""},
]
fastapi = "^0.112.2"

[tool.isort]
    """.strip()
    assert UpgradeDependencies.get_args(segment) == (
        ['"fastapi@latest"'],
        [],
        [],
        "--dev",
    )
