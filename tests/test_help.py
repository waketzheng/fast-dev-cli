from asynctor import Shell


def test_help():
    out = Shell("fast").capture_output()
    out_help = Shell("fast --help").capture_output()
    assert out.strip() == out_help.strip()
