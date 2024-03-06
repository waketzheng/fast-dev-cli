from contextlib import contextmanager

from tests.utils import capture_stdout, temp_file

from fast_tort_cli.cli import (
    GitTag,
    capture_cmd_output,
    get_current_version,
    run_and_echo,
    tag,
)


def test_tag():
    run_and_echo('git add . && git commit -m "xxx"')
    with capture_stdout() as stream:
        GitTag(message="", dry=True).run()
    assert "git tag -a" in stream.getvalue()

    with temp_file("foo.txt"):
        with capture_stdout() as stream:
            GitTag(message="", dry=True).run()

    assert "git status" in stream.getvalue()
    assert "ERROR" in stream.getvalue()

    with capture_stdout() as stream:
        tag(message="", dry=True)
    assert "git tag -a" in stream.getvalue()


def test_echo_when_not_dry(mocker):
    git_tag = GitTag("", dry=False)
    mocker.patch.object(git_tag, "mark_tag", return_value=True)
    with capture_stdout() as stream:
        git_tag.run()
    assert "poetry publish --build" in stream.getvalue()


@contextmanager
def _clear_tags():
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
