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
    assert "poetry publish --build" in capsys.readouterr().out


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
    version = get_current_version()
    prefix = "v" if "v" in capture_cmd_output(["git", "tag"]) else ""
    assert git_tag.gen() == f"git tag -a {prefix}{version} -m '' && git push --tags"
    with _clear_tags():
        git_tag_cmd = git_tag.gen()
    assert git_tag_cmd == f"git tag -a {version} -m '' && git push --tags"
    mocker.patch.object(git_tag, "has_v_prefix", return_value=True)
    tag_cmd = f"git tag -a v{version} -m '' && git push --tags"
    assert git_tag.gen() == tag_cmd
    mocker.patch.object(git_tag, "should_push", return_value=True)
    assert git_tag.gen() == tag_cmd + " && git push"
