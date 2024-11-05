from __future__ import annotations

import importlib.metadata as importlib_metadata
import os
import re
import shlex
import subprocess  # nosec:B404
import sys
from functools import cached_property
from pathlib import Path
from typing import Literal, Optional, Type, TypeAlias, get_args

import emoji
import typer
from typer import Exit, Option, echo, secho
from typer.models import OptionInfo

try:
    from . import __version__
except ImportError:  # pragma: no cover
    from importlib import import_module as _import  # For local unittest

    __version__ = _import(Path(__file__).parent.name).__version__

if sys.version_info >= (3, 11):
    from enum import StrEnum
    from typing import Annotated, Self

    import tomllib
else:  # pragma: no cover
    from enum import Enum

    import tomli as tomllib
    from typing_extensions import Annotated, Self

    class StrEnum(str, Enum):
        __str__ = str.__str__


cli = typer.Typer()
TOML_FILE = "pyproject.toml"
ToolName: TypeAlias = Literal["poetry", "pdm", "uv", ""]


def load_bool(name: str, default=False) -> bool:
    if not (v := os.getenv(name)):
        return default
    if (lower := v.lower()) in ("0", "false", "f", "off", "no", "n"):
        return False
    elif lower in ("1", "true", "t", "on", "yes", "y"):
        return True
    secho(f"WARNING: can not convert value({v!r}) of {name} to bool!")
    return default


def is_venv() -> bool:
    """Whether in a virtual environment(also work for poetry)"""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def _run_shell(cmd: list[str] | str, **kw) -> subprocess.CompletedProcess:
    if isinstance(cmd, str):
        kw.setdefault("shell", True)
    return subprocess.run(cmd, **kw)  # nosec:B603


def run_and_echo(cmd: str, *, dry=False, verbose=True, **kw) -> int:
    """Run shell command with subprocess and print it"""
    if verbose:
        echo(f"--> {cmd}")
    if dry:
        return 0
    return _run_shell(cmd, **kw).returncode


def check_call(cmd: str) -> bool:
    r = _run_shell(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.returncode == 0


def capture_cmd_output(command: list[str] | str, **kw) -> str:
    if isinstance(command, str) and not kw.get("shell"):
        command = shlex.split(command)
    r = _run_shell(command, capture_output=True, **kw)
    return r.stdout.strip().decode()


def _parse_version(line: str, pattern: re.Pattern) -> str:
    return pattern.sub("", line).split("#")[0].strip(" '\"")


def read_version_from_file(
    package_name: str, work_dir=None, toml_text: str | None = None
) -> str:
    if toml_text is None:
        toml_text = Project.load_toml_text()
    pattern = re.compile(r"version\s*=")
    invalid = ("0", "0.0.0")
    for line in toml_text.splitlines():
        if pattern.match(line):
            version = _parse_version(line, pattern)
            if version.startswith("{") or version in invalid:
                break
            return version
    if work_dir is None:
        work_dir = Project.get_work_dir()
    package_dir = work_dir / package_name
    if (
        not (init_file := package_dir / "__init__.py").exists()
        and not (init_file := work_dir / "src" / package_name / init_file.name).exists()
        and not (init_file := work_dir / "app" / init_file.name).exists()
    ):
        secho("WARNING: __init__.py file does not exist!")
        return "0.0.0"
    pattern = re.compile(r"__version__\s*=")
    for line in init_file.read_text().splitlines():
        if pattern.match(line):
            return _parse_version(line, pattern)
    secho(f"WARNING: can not find '__version__' var in {init_file}!")
    return "0.0.0"


def get_current_version(
    verbose=False, is_poetry: bool | None = None, package_name: str | None = None
) -> str:
    if is_poetry is None:
        is_poetry = Project.manage_by_poetry()
    if not is_poetry:
        work_dir = None
        if package_name is None:
            work_dir = Project.get_work_dir()
            package_name = re.sub(r"[- ]", "_", work_dir.name)
        try:
            return importlib_metadata.version(package_name)
        except importlib_metadata.PackageNotFoundError:
            return read_version_from_file(package_name, work_dir)

    cmd = ["poetry", "version", "-s"]
    if verbose:
        echo(f"--> {' '.join(cmd)}")
    if out := capture_cmd_output(cmd).strip():
        out = out.splitlines()[-1].strip().split()[-1]
    return out


def _ensure_bool(value: bool | OptionInfo) -> bool:
    if not isinstance(value, bool):
        value = getattr(value, "default", False)
    return value


def exit_if_run_failed(
    cmd: str, env=None, _exit=False, dry=False, **kw
) -> subprocess.CompletedProcess:
    run_and_echo(cmd, dry=True)
    if _ensure_bool(dry):
        return subprocess.CompletedProcess("", 0)
    if env is not None:
        env = {**os.environ, **env}
    r = _run_shell(cmd, env=env, **kw)
    if rc := r.returncode:
        if _exit:
            sys.exit(rc)
        raise Exit(rc)
    return r


class DryRun:
    def __init__(self: Self, _exit=False, dry=False) -> None:
        self.dry = dry
        self._exit = _exit

    def gen(self: Self) -> str:
        raise NotImplementedError

    def run(self: Self) -> None:
        exit_if_run_failed(self.gen(), _exit=self._exit, dry=self.dry)


class BumpUp(DryRun):
    class PartChoices(StrEnum):
        patch = "patch"
        minor = "minor"
        major = "major"

    def __init__(
        self: Self, commit: bool, part: str, filename: str | None = None, dry=False
    ) -> None:
        self.commit = commit
        self.part = part
        if filename is None:
            filename = self.parse_filename()
        self.filename = filename
        super().__init__(dry=dry)

    @staticmethod
    def get_last_commit_message() -> str:
        cmd = 'git show --pretty=format:"%s" -s HEAD'
        return capture_cmd_output(cmd)

    @classmethod
    def should_add_emoji(cls) -> bool:
        """
        If last commit message is startswith emoji,
        add a ⬆️ flag at the prefix of bump up commit message.
        """
        if out := cls.get_last_commit_message():
            return emoji.is_emoji(out[0])
        return False

    @staticmethod
    def parse_filename() -> str:
        toml_text = Project.load_toml_text()
        context = tomllib.loads(toml_text)
        try:
            ver = context["project"]["version"]
        except KeyError:
            pass
        else:
            if isinstance(ver, str) and re.match(r"\d+\.\d+\.\d+", ver):
                return TOML_FILE
        try:
            version_value = context["tool"]["poetry"]["version"]
        except KeyError:
            if not Project.manage_by_poetry():
                # version = { source = "file", path = "fast_dev_cli/__init__.py" }
                v_key = "version = "
                p_key = 'path = "'
                for line in toml_text.splitlines():
                    if not line.startswith(v_key):
                        continue
                    if p_key in (value := line.split(v_key, 1)[-1].split("#")[0]):
                        filename = value.split(p_key, 1)[-1].split('"')[0]
                        if Project.get_work_dir().joinpath(filename).exists():
                            return filename
            return TOML_FILE
        if version_value in ("0", "0.0.0"):
            try:
                package_item = context["tool"]["poetry"]["packages"]
            except KeyError:
                packages = []
            else:
                packages = [j for i in package_item if (j := i.get("include"))]
            # In case of managed by `poetry-plugin-version`
            cwd = Path.cwd()
            pattern = re.compile(r"__version__\s*=\s*['\"]")
            ds = [cwd / i for i in packages] + [cwd / cwd.name.replace("-", "_"), cwd]
            for d in ds:
                if (init_file := d / "__init__.py").exists() and pattern.search(
                    init_file.read_text()
                ):
                    break
            else:
                raise ParseError("Version file not found! Where are you now?")
            return os.path.relpath(init_file, cwd)

        return TOML_FILE

    def get_part(self, s: str) -> str:
        choices: dict[str, str] = {}
        for i, p in enumerate(self.PartChoices, 1):
            v = str(p)
            choices.update({str(i): v, v: v})
        try:
            return choices[s]
        except KeyError as e:
            echo(f"Invalid part: {s!r}")
            raise Exit(1) from e

    def gen(self: Self) -> str:
        _version = get_current_version()
        filename = self.filename
        echo(f"Current version(@{filename}): {_version}")
        if self.part:
            part = self.get_part(self.part)
        else:
            part = "patch"
            if a := input("Which one?").strip():
                part = self.get_part(a)
        self.part = part
        parse = r'--parse "(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"'
        cmd = f'bumpversion {parse} --current-version="{_version}" {part} {filename}'
        if self.commit:
            if part != "patch":
                cmd += " --tag"
            cmd += " --commit"
            if self.should_add_emoji():
                cmd += " --message-emoji=1"
            if not load_bool("DONT_GIT_PUSH"):
                cmd += " && git push && git push --tags && git log -1"
        else:
            cmd += " --allow-dirty"
        return cmd

    def run(self: Self) -> None:
        super().run()
        if not self.commit and not self.dry:
            new_version = get_current_version(True)
            echo(new_version)
            if self.part != "patch":
                echo("You may want to pin tag by `fast tag`")


@cli.command()
def version() -> None:
    """Show the version of this tool"""
    echo(f"Fast Dev Cli version: {__version__}")


@cli.command(name="bump")
def bump_version(
    part: BumpUp.PartChoices,
    commit: bool = Option(
        False, "--commit", "-c", help="Whether run `git commit` after version changed"
    ),
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
) -> None:
    """Bump up version string in pyproject.toml"""
    return BumpUp(_ensure_bool(commit), getattr(part, "value", part), dry=dry).run()


def bump() -> None:
    part, commit = "", False
    if args := sys.argv[2:]:
        if "-c" in args or "--commit" in args:
            commit = True
        for a in args:
            if not a.startswith("-"):
                part = a
                break
    return BumpUp(commit, part, dry="--dry" in args).run()


class EnvError(Exception):
    """Raise when expected to be managed by poetry, but toml file not found."""


class Project:
    path_depth = 5

    @staticmethod
    def work_dir(name: str, parent: Path, depth: int, be_file=False) -> Path | None:
        for _ in range(depth):
            if (f := parent.joinpath(name)).exists():
                if be_file:
                    return f
                return parent
            parent = parent.parent
        return None

    @classmethod
    def get_work_dir(
        cls: Type[Self],
        name=TOML_FILE,
        cwd: Path | None = None,
        allow_cwd=False,
        be_file=False,
    ) -> Path:
        cwd = cwd or Path.cwd()
        if d := cls.work_dir(name, cwd, cls.path_depth, be_file):
            return d
        if allow_cwd:
            return cls.get_root_dir(cwd)
        raise EnvError(f"{name} not found! Make sure this is a poetry project.")

    @classmethod
    def load_toml_text(cls: Type[Self], name=TOML_FILE) -> str:
        toml_file = cls.get_work_dir(name, be_file=True)
        return toml_file.read_text("utf8")

    @classmethod
    def manage_by_poetry(cls: Type[Self]) -> bool:
        return "[tool.poetry]" in cls.load_toml_text()

    @classmethod
    def get_manage_tool(cls: Type[Self]) -> ToolName:
        try:
            text = cls.load_toml_text()
        except EnvError:
            pass
        else:
            name: ToolName
            for name in get_args(ToolName):
                if f"[tool.{name}]" in text:
                    return name
        return ""

    @staticmethod
    def python_exec_dir() -> Path:
        return Path(sys.executable).parent

    @classmethod
    def get_root_dir(cls: Type[Self], cwd: Path | None = None) -> Path:
        root = cwd or Path.cwd()
        venv_parent = cls.python_exec_dir().parent.parent
        if root.is_relative_to(venv_parent):
            root = venv_parent
        return root


class ParseError(Exception):
    """Raise this if parse dependence line error"""

    ...


class UpgradeDependencies(Project, DryRun):
    class DevFlag(StrEnum):
        new = "[tool.poetry.group.dev.dependencies]"
        old = "[tool.poetry.dev-dependencies]"

    @staticmethod
    def parse_value(version_info: str, key: str) -> str:
        """Pick out the value for key in version info.

        Example::
            >>> s= 'typer = {extras = ["all"], version = "^0.9.0", optional = true}'
            >>> UpgradeDependencies.parse_value(s, 'extras')
            'all'
            >>> UpgradeDependencies.parse_value(s, 'optional')
            'true'
            >>> UpgradeDependencies.parse_value(s, 'version')
            '^0.9.0'
        """
        sep = key + " = "
        rest = version_info.split(sep, 1)[-1].strip(" =")
        if rest.startswith("["):
            rest = rest[1:].split("]")[0]
        elif rest.startswith('"'):
            rest = rest[1:].split('"')[0]
        else:
            rest = rest.split(",")[0].split("}")[0]
        return rest.strip().replace('"', "")

    @staticmethod
    def no_need_upgrade(version_info: str, line: str) -> bool:
        if (v := version_info.replace(" ", "")).startswith("{url="):
            echo(f"No need to upgrade for: {line}")
            return True
        if (f := "version=") in v:
            v = v.split(f)[1].strip('"').split('"')[0]
        if v == "*":
            echo(f"Skip wildcard line: {line}")
            return True
        elif v == "[":
            echo(f"Skip complex dependence: {line}")
            return True
        elif v.startswith(">") or v.startswith("<") or v[0].isdigit():
            echo(f"Ignore bigger/smaller/equal: {line}")
            return True
        return False

    @classmethod
    def build_args(
        cls: Type[Self], package_lines: list[str]
    ) -> tuple[list[str], dict[str, list[str]]]:
        args: list[str] = []  # ['typer[all]', 'fastapi']
        specials: dict[str, list[str]] = {}  # {'--platform linux': ['gunicorn']}
        for no, line in enumerate(package_lines, 1):
            if (
                not (m := line.strip())
                or m.startswith("#")
                or m == "]"
                or (m.startswith("{") and m.strip(",").endswith("}"))
            ):
                continue
            try:
                package, version_info = m.split("=", 1)
            except ValueError as e:
                raise ParseError(f"Failed to separate by '='@line {no}: {m}") from e
            if (package := package.strip()).lower() == "python":
                continue
            if cls.no_need_upgrade(version_info := version_info.strip(' "'), line):
                continue
            if (extras_tip := "extras") in version_info:
                package += "[" + cls.parse_value(version_info, extras_tip) + "]"
            item = f'"{package}@latest"'
            key = None
            if (pf := "platform") in version_info:
                platform = cls.parse_value(version_info, pf)
                key = f"--{pf}={platform}"
            if (sc := "source") in version_info:
                source = cls.parse_value(version_info, sc)
                key = ("" if key is None else (key + " ")) + f"--{sc}={source}"
            if "optional = true" in version_info:
                key = ("" if key is None else (key + " ")) + "--optional"
            if key is not None:
                specials[key] = specials.get(key, []) + [item]
            else:
                args.append(item)
        return args, specials

    @classmethod
    def should_with_dev(cls: Type[Self]) -> bool:
        text = cls.load_toml_text()
        return cls.DevFlag.new in text or cls.DevFlag.old in text

    @staticmethod
    def parse_item(toml_str) -> list[str]:
        lines: list[str] = []
        for line in toml_str.splitlines():
            if (line := line.strip()).startswith("["):
                if lines:
                    break
            elif line:
                lines.append(line)
        return lines

    @classmethod
    def get_args(
        cls: Type[Self], toml_text: str | None = None
    ) -> tuple[list[str], list[str], list[list[str]], str]:
        if toml_text is None:
            toml_text = cls.load_toml_text()
        main_title = "[tool.poetry.dependencies]"
        if main_title not in toml_text:
            raise EnvError(
                f"{main_title} not found! Make sure this is a poetry project."
            )
        text = toml_text.split(main_title)[-1]
        dev_flag = "--group dev"
        new_flag, old_flag = cls.DevFlag.new, cls.DevFlag.old
        if (dev_title := getattr(new_flag, "value", new_flag)) not in text:
            dev_title = getattr(old_flag, "value", old_flag)  # For poetry<=1.2
            dev_flag = "--dev"
        others: list[list[str]] = []
        try:
            main_toml, dev_toml = text.split(dev_title)
        except ValueError:
            dev_toml = ""
            main_toml = text
        mains, devs = cls.parse_item(main_toml), cls.parse_item(dev_toml)
        prod_packs, specials = cls.build_args(mains)
        if specials:
            others.extend([[k] + v for k, v in specials.items()])
        dev_packs, specials = cls.build_args(devs)
        if specials:
            others.extend([[k] + v + [dev_flag] for k, v in specials.items()])
        return prod_packs, dev_packs, others, dev_flag

    @classmethod
    def gen_cmd(cls: Type[Self]) -> str:
        main_args, dev_args, others, dev_flags = cls.get_args()
        return cls.to_cmd(main_args, dev_args, others, dev_flags)

    @staticmethod
    def to_cmd(
        main_args: list[str],
        dev_args: list[str],
        others: list[list[str]],
        dev_flags: str,
    ) -> str:
        command = "poetry add "
        _upgrade = ""
        if main_args:
            _upgrade = command + " ".join(main_args)
        if dev_args:
            if _upgrade:
                _upgrade += " && "
            _upgrade += command + dev_flags + " " + " ".join(dev_args)
        for single in others:
            _upgrade += f" && poetry add {' '.join(single)}"
        return _upgrade

    def gen(self: Self) -> str:
        return self.gen_cmd() + " && poetry lock && poetry update"


@cli.command()
def upgrade(
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
) -> None:
    """Upgrade dependencies in pyproject.toml to latest versions"""
    UpgradeDependencies(dry=dry).run()


class GitTag(DryRun):
    def __init__(self: Self, message: str, dry: bool) -> None:
        self.message = message
        super().__init__(dry=dry)

    @staticmethod
    def has_v_prefix() -> bool:
        return "v" in capture_cmd_output("git tag")

    def should_push(self: Self) -> bool:
        return "git push" in self.git_status

    def gen(self: Self) -> str:
        _version = get_current_version(verbose=False)
        if self.has_v_prefix():
            # Add `v` at prefix to compare with bumpversion tool
            _version = "v" + _version
        cmd = f"git tag -a {_version} -m {self.message!r} && git push --tags"
        if self.should_push():
            cmd += " && git push"
        return cmd

    @cached_property
    def git_status(self: Self) -> str:
        return capture_cmd_output("git status")

    def mark_tag(self: Self) -> bool:
        if not re.search(r"working (tree|directory) clean", self.git_status) and (
            "无文件要提交，干净的工作区" not in self.git_status
        ):
            run_and_echo("git status")
            echo("ERROR: Please run git commit to make sure working tree is clean!")
            return False
        return bool(super().run())

    def run(self: Self) -> None:
        if self.mark_tag() and not self.dry:
            echo("You may want to publish package:\n poetry publish --build")


@cli.command()
def tag(
    message: str = Option("", "-m", "--message"),
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
) -> None:
    """Run shell command: git tag -a <current-version-in-pyproject.toml> -m {message}"""
    GitTag(message, dry=dry).run()


class LintCode(DryRun):
    def __init__(
        self: Self,
        args,
        check_only=False,
        _exit=False,
        dry=False,
        bandit=False,
        skip_mypy=False,
    ) -> None:
        self.args = args
        self.check_only = check_only
        self._bandit = bandit
        self._skip_mypy = skip_mypy
        super().__init__(_exit, dry)

    @staticmethod
    def check_lint_tool_installed() -> bool:
        return check_call("ruff --version")

    @staticmethod
    def prefer_dmypy(paths: str, tools: list[str]) -> bool:
        return (
            paths == "."
            and any(t.startswith("mypy") for t in tools)
            and not load_bool("NO_DMYPY")
        )

    @staticmethod
    def get_package_name() -> str:
        root = Project.get_work_dir(allow_cwd=True)
        package_maybe = (root.name.replace("-", "_"), "src")
        for name in package_maybe:
            if root.joinpath(name).is_dir():
                return name
        return "."

    @classmethod
    def to_cmd(
        cls: Type[Self], paths=".", check_only=False, bandit=False, skip_mypy=False
    ) -> str:
        cmd = ""
        tools = ["ruff format", "ruff check --extend-select=I,B,SIM --fix", "mypy"]
        if check_only:
            tools[0] += " --check"
        if check_only or load_bool("NO_FIX"):
            tools[1] = tools[1].replace(" --fix", "")
        if skip_mypy or load_bool("SKIP_MYPY"):
            # Sometimes mypy is too slow
            tools = tools[:-1]
        elif load_bool("IGNORE_MISSING_IMPORTS"):
            tools[-1] += " --ignore-missing-imports"
        lint_them = " && ".join("{0}{%d} {1}" % i for i in range(2, len(tools) + 2))
        prefix = ""
        should_run_by_tool = False
        if is_venv():
            if not cls.check_lint_tool_installed():
                should_run_by_tool = True
                if check_call('python -c "import fast_dev_cli"'):
                    command = 'python -m pip install -U "fast_dev_cli"'
                    tip = "You may need to run following command to install lint tools:"
                    secho(f"{tip}\n\n  {command}\n", fg="yellow")
        else:
            should_run_by_tool = True
        if should_run_by_tool:
            prefix = Project.get_manage_tool() + " run "
        if cls.prefer_dmypy(paths, tools):
            tools[-1] = "dmypy run"
        cmd += lint_them.format(prefix, paths, *tools)
        if bandit or load_bool("FASTDEVCLI_BANDIT"):
            command = prefix + "bandit"
            if paths == ".":  # fast check --bandit
                command += " -r " + cls.get_package_name()
                cmd += " && " + command
        return cmd

    def gen(self: Self) -> str:
        paths = " ".join(map(str, self.args)) if self.args else "."
        return self.to_cmd(paths, self.check_only, self._bandit, self._skip_mypy)


def parse_files(args: list[str] | tuple[str, ...]) -> list[str]:
    return [i for i in args if not i.startswith("-")]


def lint(files=None, dry=False, skip_mypy=False) -> None:
    if files is None:
        files = parse_files(sys.argv[1:])
    if files and files[0] == "lint":
        files = files[1:]
    LintCode(files, dry=dry, skip_mypy=skip_mypy).run()


def check(files=None, dry=False, bandit=False, skip_mypy=False) -> None:
    LintCode(
        files, check_only=True, _exit=True, dry=dry, bandit=bandit, skip_mypy=skip_mypy
    ).run()


@cli.command(name="lint")
def make_style(
    files: Annotated[Optional[list[Path]], typer.Argument()] = None,
    check_only: bool = Option(False, "--check-only", "-c"),
    skip_mypy: bool = Option(False, "--skip-mypy"),
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
) -> None:
    """Run: ruff check/format to reformat code and then mypy to check"""
    if files is None:
        files = [Path(".")]
    elif isinstance(files, str):
        files = [files]
    skip = _ensure_bool(skip_mypy)
    if _ensure_bool(check_only):
        check(files, dry=dry, skip_mypy=skip)
    else:
        lint(files, dry=dry, skip_mypy=skip)


@cli.command(name="check")
def only_check(
    bandit: bool = Option(False, "--bandit", help="Run `bandit -r <package_dir>`"),
    skip_mypy: bool = Option(False, "--skip-mypy"),
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
) -> None:
    """Check code style without reformat"""
    check(dry=dry, bandit=bandit, skip_mypy=_ensure_bool(skip_mypy))


class Sync(DryRun):
    def __init__(self: Self, filename: str, extras: str, save: bool, dry=False) -> None:
        self.filename = filename
        self.extras = extras
        self._save = save
        super().__init__(dry=dry)

    def gen(self) -> str:
        extras, save = self.extras, self._save
        should_remove = not Path.cwd().joinpath(self.filename).exists()
        if not (tool := Project.get_manage_tool()):
            if should_remove or not is_venv():
                raise EnvError("There project is not managed by uv/pdm/poetry!")
            return f"python -m pip install -r {self.filename}"
        prefix = "" if is_venv() else f"{tool} run "
        ensurepip = " {1}python -m ensurepip && {1}python -m pip install -U pip &&"
        if tool == "uv":
            export_cmd = "uv export --no-hashes --all-extras --frozen"
            if check_call(prefix + "python -m pip --version"):
                ensurepip = ""
        elif tool in ("poetry", "pdm"):
            export_cmd = f"{tool} export --without-hashes --with=dev"
            if tool == "poetry":
                ensurepip = ""
                if not UpgradeDependencies.should_with_dev():
                    export_cmd = export_cmd.replace(" --with=dev", "")
                if extras and isinstance(extras, str | list):
                    export_cmd += f" --{extras=}".replace("'", '"')
            elif check_call(prefix + "python -m pip --version"):
                ensurepip = ""
        install_cmd = "{2} -o {0} &&%s {1}python -m pip install -r {0}" % ensurepip
        if should_remove and not save:
            install_cmd += " && rm -f {0}"
        return install_cmd.format(self.filename, prefix, export_cmd)


@cli.command()
def sync(
    filename="dev_requirements.txt",
    extras: str = Option("", "--extras", "-E"),
    save: bool = Option(
        False, "--save", "-s", help="Whether save the requirement file"
    ),
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
) -> None:
    """Export dependencies by poetry to a txt file then install by pip."""
    Sync(filename, extras, save, dry=dry).run()


def _should_run_test_script(path: Path = Path("scripts")) -> Path | None:
    for name in ("test.sh", "test.py"):
        if (file := path / name).exists():
            return file
    return None


def test(dry: bool, ignore_script=False) -> None:
    cwd = Path.cwd()
    root = Project.get_work_dir(cwd=cwd, allow_cwd=True)
    script_dir = root / "scripts"
    if not _ensure_bool(ignore_script) and (
        test_script := _should_run_test_script(script_dir)
    ):
        cmd = f"{os.path.relpath(test_script, root)}"
        if cwd != root:
            cmd = f"cd {root} && " + cmd
    else:
        cmd = 'coverage run -m pytest -s && coverage report --omit="tests/*" -m'
        if not is_venv() or not check_call("coverage --version"):
            sep = " && "
            tool = Project.get_manage_tool()
            cmd = sep.join(f"{tool} run " + i for i in cmd.split(sep))
    exit_if_run_failed(cmd, dry=dry)


@cli.command(name="test")
def coverage_test(
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
    ignore_script: bool = Option(False, "--ignore-script", "-i"),
) -> None:
    """Run unittest by pytest and report coverage"""
    return test(dry, ignore_script)


class Publish:
    class CommandEnum(StrEnum):
        poetry = "poetry publish --build"
        pdm = "pdm publish"
        uv = "uv build && uv publish"
        twine = "python -m build && twine upload"

    @classmethod
    def gen(cls) -> str:
        if (tool := Project.get_manage_tool()) and tool in get_args(ToolName):
            return cls.CommandEnum[tool]
        return cls.CommandEnum.twine


@cli.command()
def upload(
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
) -> None:
    """Shortcut for package publish"""
    cmd = Publish.gen()
    exit_if_run_failed(cmd, dry=dry)


def dev(
    port: int | None | OptionInfo,
    host: str | None | OptionInfo,
    file: Optional[str] = None,
    dry=False,
) -> None:
    cmd = "fastapi dev"
    no_port_yet = True
    if file is not None:
        try:
            port = int(file)  # type:ignore[arg-type]
        except ValueError:
            cmd += f" {file}"
        else:
            if port != 8000:
                cmd += f" --port={port}"
                no_port_yet = False
    if no_port_yet and (port := getattr(port, "default", port)) and str(port) != "8000":
        cmd += f" --port={port}"
    if (host := getattr(host, "default", host)) and host not in (
        "localhost",
        "127.0.0.1",
    ):
        cmd += f" --host={host}"
    exit_if_run_failed(cmd, dry=dry)


@cli.command(name="dev")
def runserver(
    file_or_port: Annotated[Optional[str], typer.Argument()] = None,
    port: Optional[int] = Option(None, "-p", "--port"),
    host: Optional[str] = Option(None, "-h", "--host"),
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
) -> None:
    """Start a fastapi server(only for fastapi>=0.111.0)"""
    if file_or_port:
        dev(port, host, file=file_or_port, dry=dry)
    else:
        dev(port, host, dry=dry)


def main() -> None:
    cli()


if __name__ == "__main__":  # pragma: no cover
    main()
