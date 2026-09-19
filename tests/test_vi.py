from fast_dev_cli.cli import capture_cmd_output


def test_fast_vi_md() -> None:
    cmd = "fast vi README --dry"
    cmd2 = "fast vi README. --dry"
    cmd3 = "fast vi README.md --dry"
    expected = "--> vim README.md"
    assert capture_cmd_output(cmd) == expected 
    assert capture_cmd_output(cmd2) == expected 
    assert capture_cmd_output(cmd3) == expected 

def test_fast_vi_py() -> None:
    cmd = "fast vi fast_dev_cli/cli --dry"
    cmd2 = "fast vi fast_dev_cli/cli. --dry"
    cmd3 = "fast vi fast_dev_cli/cli.py --dry"
    expected = "--> vim fast_dev_cli/cli.py"
    assert capture_cmd_output(cmd) == expected 
    assert capture_cmd_output(cmd2) == expected 
    assert capture_cmd_output(cmd3) == expected 

def test_fast_vi_multi() -> None:
    cmd = "fast vi fast_dev_cli/cli README --dry"
    cmd2 = "fast vi fast_dev_cli/cli. README.md --dry"
    cmd3 = "fast vi fast_dev_cli/cli.py README. --dry"
    expected = "--> vim -O fast_dev_cli/cli.py README.md"
    assert capture_cmd_output(cmd) == expected 
    assert capture_cmd_output(cmd2) == expected 
    assert capture_cmd_output(cmd3) == expected 
