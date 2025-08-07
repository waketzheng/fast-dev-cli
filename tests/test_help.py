from .utils import get_cmd_output


def test_help():
    out = get_cmd_output("fast")
    out_help = get_cmd_output("fast --help")
    assert out == out_help
