import importlib.metadata
import os
import re
import subprocess
import sys
from enum import StrEnum
from functools import cached_property
from pathlib import Path
from subprocess import CompletedProcess

__version__ = importlib.metadata.version(Path(__file__).parent.name)


def parse_files(args: list[str] | tuple[str, ...]) -> list[str]:
    return [i for i in args if not i.startswith("-")]


try:
    import typer
    from typer import Exit, Option, echo, secho

    cli = typer.Typer()
    if len(sys.argv) >= 2 and sys.argv[1] == "lint":
        if not parse_files(sys.argv[2:]):
            sys.argv.append(".")
except ModuleNotFoundError:
    import click
    from click import echo, secho
    from click.core import Group as _Group
    from click.exceptions import Exit

    def Option(default, *shortcuts, help=None):  # type:ignore[no-redef]
        return default

    def _command(self, *args, **kwargs):
        from click.decorators import command

        def decorator(f):
            if kwargs.get("name") == "lint":
                import functools

                def auto_fill_args(func):
                    @functools.wraps(func)
                    def runner(*arguments: str, **kw):
                        if "files" not in kw and not parse_files(arguments):
                            arguments = (".",)
                        return func(*arguments, **kw)

                    return runner

                f = auto_fill_args(f)
                if sys.argv[2:]:
                    f = click.argument("files", nargs=-1)(f)
            cmd = command(*args, **kwargs)(f)
            self.add_command(cmd)
            return cmd

        return decorator

    _Group.command = _command  # type:ignore

    @click.group()
    def cli() -> None: ...  # pragma: no cover


TOML_FILE = "pyproject.toml"


def load_bool(name: str, default=False) -> bool:
    if not (v := os.getenv(name)):
        return default
    return v.lower() not in ("0", "false", "off", "no", "n")


def is_venv() -> bool:
    """Whether in a virtual environment(also work for poetry)"""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def _run_shell(cmd: str, **kw) -> CompletedProcess:
    kw.setdefault("shell", True)
    return subprocess.run(cmd, **kw)


def run_and_echo(cmd: str, *, dry=False, verbose=True, **kw) -> int:
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
        command = command.split()
    r = subprocess.run(command, capture_output=True, **kw)
    return r.stdout.strip().decode()


def get_current_version(verbose=False) -> str:
    cmd = ["poetry", "version", "-s"]
    if verbose:
        command = " ".join(cmd)
        echo(f"--> {command}")
    return capture_cmd_output(cmd)


def exit_if_run_failed(
    cmd: str, env=None, _exit=False, dry=False, **kw
) -> CompletedProcess:
    run_and_echo(cmd, dry=True)
    if dry:
        return CompletedProcess("", 0)
    if env is not None:
        env = {**os.environ, **env}
    r = _run_shell(cmd, env=env, **kw)
    if rc := r.returncode:
        if _exit:
            sys.exit(rc)
        raise Exit(rc)
    return r


class DryRun:
    def __init__(self, _exit=False, dry=False):
        self.dry = dry
        self._exit = _exit

    def gen(self) -> str:
        raise NotImplementedError

    def run(self) -> None:
        exit_if_run_failed(self.gen(), _exit=self._exit, dry=self.dry)


class BumpUp(DryRun):
    class PartChoices(StrEnum):
        patch = "patch"
        minor = "minor"
        major = "major"

    def __init__(self, commit: bool, part: str, filename=TOML_FILE, dry=False):
        self.commit = commit
        self.part = part
        self.filename = filename
        super().__init__(dry=dry)

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

    def gen(self) -> str:
        _version = get_current_version()
        filename = self.filename
        echo(f"Current version(@{filename}): {_version}")
        if self.part:
            part = self.get_part(self.part)
        else:
            tip = "Which one?"
            if a := input(tip).strip():
                part = self.get_part(a)
            else:
                part = "patch"
        self.part = part
        parse = r'--parse "(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"'
        cmd = f'bumpversion {parse} --current-version="{_version}" {part} {filename}'
        if self.commit:
            if part != "patch":
                cmd += " --tag"
            cmd += " --commit && git push && git push --tags && git log -1"
        else:
            cmd += " --allow-dirty"
        return cmd

    def run(self) -> None:
        super().run()
        if not self.commit and not self.dry:
            new_version = get_current_version(True)
            echo(new_version)
            if self.part != "patch":
                echo("You may want to pin tag by `fast tag`")


@cli.command()
def version():
    """Show the version of this tool"""
    echo(__version__)


@cli.command(name="bump")
def bump_version(
    part: BumpUp.PartChoices,
    commit: bool = Option(
        False, "--commit", "-c", help="Whether run `git commit` after version changed"
    ),
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
):
    return BumpUp(commit, part.value, dry=dry).run()


def bump():
    part, commit = "", False
    if args := sys.argv[2:]:
        if "-c" in args or "--commit" in args:
            commit = True
        for a in args:
            if not a.startswith("-"):
                part = a
                break
    return BumpUp(commit, part, dry="--dry" in args).run()


class EnvError(Exception): ...


class Project:
    path_depth = 5

    @staticmethod
    def work_dir(name: str, parent: Path, depth: int) -> Path | None:
        for _ in range(depth):
            if parent.joinpath(name).exists():
                return parent
            parent = parent.parent
        return None

    @classmethod
    def get_work_dir(cls, name=TOML_FILE, cwd: Path | None = None) -> Path:
        if d := cls.work_dir(name, cwd or Path.cwd(), cls.path_depth):
            return d
        raise EnvError(f"{name} not found! Make sure this is a poetry project.")

    @classmethod
    def load_toml_text(cls):
        toml_file = cls.get_work_dir().resolve() / TOML_FILE  # to be optimize
        return toml_file.read_text("utf8")

    @staticmethod
    def python_exec_dir() -> Path:
        return Path(sys.executable).parent

    @classmethod
    def get_root_dir(cls, cwd: Path | None = None) -> Path:
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
        elif v.startswith(">") or v.startswith("<") or v[0].isdigit():
            echo(f"Ignore bigger/smaller/equal: {line}")
            return True
        return False

    @classmethod
    def build_args(
        cls, package_lines: list[str]
    ) -> tuple[list[str], dict[str, list[str]]]:
        args: list[str] = []  # ['typer[all]', 'fastapi']
        specials: dict[str, list[str]] = {}  # {'--platform linux': ['gunicorn']}
        for line in package_lines:
            if not (m := line.strip()) or m.startswith("#"):
                continue
            try:
                package, version_info = m.split("=", 1)
            except ValueError as e:
                raise ParseError(f"{m = }") from e
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
    def should_with_dev(cls):
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
        cls, toml_text: str | None = None
    ) -> tuple[list[str], list[str], list[list[str]], str]:
        if toml_text is None:
            toml_text = cls.load_toml_text()
        main_title = "[tool.poetry.dependencies]"
        text = toml_text.split(main_title)[-1]
        dev_flag = "--group dev"
        if (dev_title := cls.DevFlag.new.value) not in text:
            dev_title = cls.DevFlag.old.value  # For poetry<=1.2
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
    def gen_cmd(cls) -> str:
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

    def gen(self) -> str:
        return self.gen_cmd()


@cli.command()
def upgrade(
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
):
    """Upgrade dependencies in pyproject.toml to latest versions"""
    UpgradeDependencies(dry=dry).run()


class GitTag(DryRun):
    def __init__(self, message, dry):
        self.message = message
        super().__init__(dry=dry)

    def has_v_prefix(self) -> bool:
        return "v" in capture_cmd_output("git tag")

    def should_push(self) -> bool:
        return "git push" in self.git_status

    def gen(self):
        _version = get_current_version(verbose=False)
        if self.has_v_prefix():
            # Add `v` at prefix to compare with bumpversion tool
            _version = "v" + _version
        cmd = f"git tag -a {_version} -m {self.message!r} && git push --tags"
        if self.should_push():
            cmd += " && git push"
        return cmd

    @cached_property
    def git_status(self) -> str:
        return capture_cmd_output("git status")

    def mark_tag(self) -> bool:
        if not re.search(r"working (tree|directory) clean", self.git_status):
            run_and_echo("git status")
            echo("ERROR: Please run git commit to make sure working tree is clean!")
            return False
        return bool(super().run())

    def run(self):
        if self.mark_tag() and not self.dry:
            echo("You may want to publish package:\n poetry publish --build")


@cli.command()
def tag(
    message: str = Option("", "-m", "--message"),
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
):
    """Run shell command: git tag -a <current-version-in-pyproject.toml> -m {message}"""
    GitTag(message, dry=dry).run()


class LintCode(DryRun):
    def __init__(self, args, check_only=False, _exit=False, dry=False):
        self.args = args
        self.check_only = check_only
        super().__init__(_exit, dry)

    @staticmethod
    def check_lint_tool_installed() -> bool:
        return check_call("black --version")

    @classmethod
    def to_cmd(cls, paths=".", check_only=False):
        cmd = ""
        tools = ["isort --profile=black", "black", "ruff check --fix", "mypy"]
        if check_only:
            tools[0] += " --check-only"
            tools[1] += " --check --fast"
        if check_only or load_bool("NO_FIX"):
            tools[2] = tools[2].replace(" --fix", "")
        if load_bool("SKIP_MYPY"):
            # Sometimes mypy is too slow
            tools = tools[:-1]
        lint_them = " && ".join("{0}{%d} {1}" % i for i in range(2, len(tools) + 2))
        current_path = Path.cwd()
        try:
            root = Project.get_work_dir(cwd=current_path)
        except EnvError:
            root = Project.get_root_dir(cwd=current_path)
        app_name = root.name.replace("-", "_")
        if (app_dir := root / app_name).exists() or (app_dir := root / "app").exists():
            if current_path == app_dir:
                tools[0] += " --src=."
            elif current_path == root:
                tools[0] += f" --src={app_dir.name}"
            else:
                parents = "../"
                for i, p in enumerate(current_path.parents):
                    if p == root:
                        parents *= i + 1
                        break
                tools[0] += f" --src={parents}{app_dir.name}"
        prefix = "poetry run "
        if is_venv():
            if cls.check_lint_tool_installed():
                prefix = ""
            else:
                if check_call("python -c 'import fast_dev_cli'"):
                    command = 'python -m pip install -U "fast_dev_cli[all]"'
                    tip = "You may need to run the following command to install lint tools"
                    secho(f"{tip}:\n\n  {command}\n", fg="yellow")
        cmd += lint_them.format(prefix, paths, *tools)
        return cmd

    def gen(self) -> str:
        paths = " ".join(self.args) if self.args else "."
        return self.to_cmd(paths, self.check_only)


def lint(files=None, dry=False):
    if files is None:
        files = parse_files(sys.argv[1:])
    LintCode(files, dry=dry).run()


def check(files=None, dry=False):
    LintCode(files, check_only=True, _exit=True, dry=dry).run()


@cli.command(name="lint")
def make_style(
    files: list[str],
    check_only: bool = Option(False, "--check-only", "-c"),
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
):
    """Run: isort+black+ruff to reformat code and then mypy to check"""
    if isinstance(files, str):
        files = [files]
    if check_only:
        check(files, dry=dry)
    else:
        lint(files, dry=dry)


@cli.command(name="check")
def only_check(
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
):
    """Check code style without reformat"""
    check(dry=dry)


class Sync(DryRun):
    def __init__(self, filename: str, extras: str, save: bool, dry=False):
        self.filename = filename
        self.extras = extras
        self._save = save
        super().__init__(dry=dry)

    def gen(self) -> str:
        extras, save = self.extras, self._save
        should_remove = not Path.cwd().joinpath(self.filename).exists()
        prefix = "" if is_venv() else "poetry run "
        install_cmd = (
            "poetry export --with=dev --without-hashes -o {0}"
            " && {1}pip install -r {0}"
        )
        if not UpgradeDependencies.should_with_dev():
            install_cmd = install_cmd.replace(" --with=dev", "")
        if extras and isinstance(extras, str | list):
            install_cmd = install_cmd.replace("export", f"export --{extras=}")
        if should_remove and not save:
            install_cmd += " && rm -f {0}"
        return install_cmd.format(self.filename, prefix)


@cli.command()
def sync(
    filename="dev_requirements.txt",
    extras: str = Option("", "--extras", "-E"),
    save: bool = Option(
        False, "--save", "-s", help="Whether save the requirement file"
    ),
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
):
    """Export dependencies by poetry to a txt file then install by pip."""
    Sync(filename, extras, save, dry=dry).run()


@cli.command()
def test(
    dry: bool = Option(False, "--dry", help="Only print, not really run shell command"),
):
    """Run unittest by pytest and report coverage"""
    cmd = 'coverage run -m pytest -s && coverage report --omit="tests/*" -m'
    if not is_venv() or not check_call("coverage --version"):
        sep = " && "
        cmd = sep.join("poetry run " + i for i in cmd.split(sep))
    exit_if_run_failed(cmd, dry=dry)


if __name__ == "__main__":
    cli()  # pragma: no cover
