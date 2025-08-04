import pytest

from fast_dev_cli.cli import Exit, capture_cmd_output, run_by_subprocess


def test_exec_dry():
    out = capture_cmd_output('fast exec "echo hello" --dry')
    assert "--> echo hello" in out
    assert out.count("hello") == 1
    out = capture_cmd_output('fast exec "echo hello|grep h" --dry')
    assert "--> echo hello|grep h" in out
    assert out.count("hello") == 1
    out = capture_cmd_output(
        'fast exec "invalid command" --dry && echo success || echo failed', shell=True
    )
    assert "success" in out
    assert "failed" not in out


def test_exec():
    out = capture_cmd_output('fast exec "echo hello"')
    assert "--> echo hello" in out
    assert out.count("hello") == 2
    out = capture_cmd_output('fast exec "echo hello|grep h"')
    assert "--> echo hello|grep h" in out
    assert out.count("hello") == 2
    out = capture_cmd_output(
        'fast exec "invalid command" && echo success || echo failed', shell=True
    )
    assert "failed" in out
    assert "success" not in out


def test_run_by_subprocess():
    with pytest.raises(Exit):
        run_by_subprocess("python -c 'import sys;sys.exit(1)'")
    with pytest.raises(Exit):
        run_by_subprocess("cd not-exit-dir")
    assert not run_by_subprocess(f"cat {__file__}|grep xxx")
