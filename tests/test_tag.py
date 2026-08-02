import shlex
import sys
from contextlib import contextmanager

from fast_dev_cli.cli import (
    GitTag,
    capture_cmd_output,
    get_current_version,
    run_and_echo,
    tag,
)
from tests.utils import capture_stdout, temp_file


def test_tag():
    run_and_echo('git add . && git commit -m "xxx"')
    with capture_stdout() as stream:
        GitTag(message="", dry=True).run()
    assert "git tag -a" in stream.getvalue()

    with temp_file("foo.txt"), capture_stdout() as stream:
        GitTag(message="", dry=True).run()

    assert "git status" in stream.getvalue()
    assert "ERROR" in stream.getvalue()

    with capture_stdout() as stream:
        tag(message="", dry=True)
    assert "git tag -a" in stream.getvalue()


def test_echo_when_not_dry(mocker, capsys):
    git_tag = GitTag("", dry=False)
    mocker.patch.object(git_tag, "mark_tag", return_value=True)
    git_tag.run()
    assert "pdm publish" in capsys.readouterr().out


def test_tag_quotes_message(mocker):
    message = "release $(echo injected) & next"
    git_tag = GitTag(message, dry=True)
    mocker.patch("fast_dev_cli.cli.get_current_version", return_value=(False, "1.2.3"))
    mocker.patch.object(git_tag, "has_v_prefix", return_value=False)
    mocker.patch.object(git_tag, "should_push", return_value=False)
    tag_command = git_tag.gen().split(" && ", 1)[0]
    assert shlex.split(tag_command) == [
        "git",
        "tag",
        "-a",
        "1.2.3",
        "-m",
        message,
    ]


@contextmanager
def _clear_tags():
    if sys.platform == "win32":
        for t in capture_cmd_output("git tag").splitlines():
            if "v" in (tag := t.strip()):
                run_and_echo(f"git tag -d {tag}")
    else:
        run_and_echo("git tag | xargs git tag -d")
    yield
    run_and_echo("git pull --tags")


def test_with_push(mocker):
    git_tag = GitTag("", dry=True)
    mocker.patch.object(git_tag, "git_status", return_value="git push")
    should_sync, version = get_current_version(check_version=True)
    prefix = "v" if "v" in capture_cmd_output(["git", "tag"]) else ""
    sync = "pdm sync --prod"
    push = "git push --tags"
    expected = f"git tag -a {prefix}{version} -m '' && {push}"
    if should_sync:
        expected = f"{sync} && " + expected
    assert git_tag.gen() == expected
    with _clear_tags():
        git_tag_cmd = git_tag.gen()
    expected = f"git tag -a {version} -m '' && {push}"
    if should_sync:
        expected = f"{sync} && " + expected
    assert git_tag_cmd == expected
    mocker.patch.object(git_tag, "has_v_prefix", return_value=True)
    expected = f"git tag -a v{version} -m '' && {push}"
    if should_sync:
        expected = f"{sync} && " + expected
    assert git_tag.gen() == expected
    mocker.patch.object(git_tag, "should_push", return_value=True)
    assert git_tag.gen() == expected + " && git push"
