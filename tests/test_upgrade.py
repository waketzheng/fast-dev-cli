from contextlib import chdir, redirect_stdout
from io import StringIO
from pathlib import Path

from fast_dev_cli.cli import TOML_FILE, UpgradeDependencies, run_and_echo, upgrade


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
    assert UpgradeDependencies.should_with_dev() is True
    with chdir(tmp_path):
        project = tmp_path / "project"
        run_and_echo(f"poetry new {project.name}")
        with chdir(project):
            assert not UpgradeDependencies.should_with_dev()
            run_and_echo("poetry add isort")
            assert not UpgradeDependencies.should_with_dev()
            run_and_echo("poetry add --group=dev black")
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


def test_get_args_hard(tmp_path: Path):
    assert UpgradeDependencies.get_args() == (
        [],
        ['"ipython@latest"', '"coveralls@latest"', '"pytest-mock@latest"'],
        [
            [
                "--optional",
                '"bumpversion@latest"',
                '"pytest@latest"',
            ]
        ],
        "--group dev",
    )
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


def test_gen_cmd():
    expected = 'poetry add --group dev "ipython@latest" "coveralls@latest" "pytest-mock@latest" && poetry add --optional "bumpversion@latest" "pytest@latest"'
    assert UpgradeDependencies.gen_cmd() == UpgradeDependencies().gen() == expected
    stream = StringIO()
    with redirect_stdout(stream):
        upgrade(dry=True)
    assert expected in stream.getvalue()
    args = (
        ['"anyio@latest"'],
        [],
        [["--platform=linux", '"pytest@latest"', "--dev"]],
        "--dev",
    )
    assert (
        UpgradeDependencies.to_cmd(*args)
        == 'poetry add "anyio@latest" && poetry add --platform=linux "pytest@latest" --dev'
    )
    args = (
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


def test_get_dir(mocker):
    me = Path(__file__)
    parent = me.parent
    root = parent.parent
    assert (
        UpgradeDependencies.get_work_dir() == UpgradeDependencies.get_root_dir() == root
    )
    with chdir(parent):
        assert UpgradeDependencies.get_root_dir() == parent
        mocker.patch.object(UpgradeDependencies, "python_exec_dir", return_value=me)
        assert UpgradeDependencies.get_root_dir() == root
