"""."""

from binary_classification_ratios.cli.cmd_line import CmdLine, get_cmd_line


def test_cmd_line_short_args() -> None:
    """."""
    cli = get_cmd_line(
        ['-tp', '1', '-tn', '2', '-fp', '3', '-fn', '4', '--fmt', '.4f', '--accuracy-fmt', '.6f']
    )
    assert isinstance(cli, CmdLine)
    assert cli.tp == 1
    assert cli.tn == 2
    assert cli.fp == 3
    assert cli.fn == 4
    assert cli.fmt == '.4f'
    assert cli.accuracy_fmt == '.6f'


def test_cmd_line_no_args() -> None:
    """."""
    cli = get_cmd_line([])
    assert cli.tp == 0
    assert cli.tn == 0
    assert cli.fn == 0
    assert cli.fp == 0
    assert cli.accuracy_fmt == '.5f'
    assert cli.fmt == '.3f'
