"""."""

from argparse import ArgumentParser
from typing import Sequence, Union


PROG = 'binary-classification-ratios'
HLP_FMT = 'Format for the recall, precision and F1-score.'


class CmdLine:
    """."""

    def __init__(self) -> None:
        self.tp: int = 0
        self.tn: int = 0
        self.fp: int = 0
        self.fn: int = 0
        self.fmt: str = '.3f'
        self.accuracy_fmt: str = '.5f'


def get_cmd_line(args: Union[Sequence[str], None] = None) -> CmdLine:
    """."""
    parser = ArgumentParser(PROG, f'{PROG} [OPTIONS]')
    parser.add_argument('-tp', type=int, default=0, help='Number of true positives.')
    parser.add_argument('-tn', type=int, default=0, help='Number of true negatives.')
    parser.add_argument('-fp', type=int, default=0, help='Number of false positives.')
    parser.add_argument('-fn', type=int, default=0, help='Number of false negatives.')
    parser.add_argument('--fmt', help=HLP_FMT)
    parser.add_argument('--accuracy-fmt', help='Format for the accuracy.')
    namespace = CmdLine()
    parser.parse_args(args, namespace=namespace)
    return namespace
