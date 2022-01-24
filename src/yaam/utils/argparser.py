'''
Command line arguments parser
'''

from argparse import ArgumentParser, Namespace, SUPPRESS
from typing import Sequence
from yaam.model.options import OptionGroup


class Parser(object):
    '''
    Yaam command line arguments parser
    '''
    def __init__(self) -> None:
        super().__init__()

        self.__parser = ArgumentParser(prog="YAAM", description="Yet Another Addon Manager")

        for opt_group in OptionGroup:

            parse_group = self.__parser
            if opt_group.is_mutally_exclusive():
                parse_group = self.__parser.add_mutually_exclusive_group()

            for opt in opt_group.options:
                parse_group.add_argument(
                    *[f"--{alias}" if len(alias) > 2 else f"-{alias}" for alias in opt.aliases],
                    action=opt.action,
                    help=opt.descr,
                    default=SUPPRESS
                )

    def parse(self, args: Sequence[str]) -> Namespace:
        '''
        Parser command line arguments
        '''
        return self.__parser.parse_args(args)

    def underlying_parser(self) -> ArgumentParser:
        '''
        Return parsed arguments
        '''
        return self.__parser
