'''
Command line arguments parser
'''
import argparse
from typing import Sequence
from yaam.model.options import OptionGroup

class Parser(object):
    '''
    Yaam command line arguments parser
    '''
    def __init__(self) -> None:
        super().__init__()

        self.__parser = argparse.ArgumentParser(prog="YAAM", description="Yet Another Addon Manager" )

        for opt_group in OptionGroup:

            parse_group = self.__parser
            if opt_group.is_mutally_exclusive():
                parse_group = self.__parser.add_mutually_exclusive_group()

            for opt in opt_group.options:
                parse_group.add_argument(
                    *[f"--{alias}" if len(alias) > 1 else f"-{alias}" for alias in opt.aliases],
                    action=opt.action,
                    help=opt.descr,
                    default=opt.default
                )

    def parse(self, args: Sequence[str]) -> argparse.Namespace:
        '''
        Parser command line arguments
        '''
        return self.__parser.parse_args(args)

    def args(self):
        '''
        Return parsed arguments
        '''
        return self.__parser
        