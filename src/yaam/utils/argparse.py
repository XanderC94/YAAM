'''
Command line arguments parser
'''
import argparse
from typing import Sequence

class Parser(object):
    '''
    Yaam command line arguments parser
    '''
    def __init__(self) -> None:
        super().__init__()
        self.__parser = argparse.ArgumentParser(prog="YAAM", description="Yet Another Addon Manager" )

        self.__parser.add_argument(
            "--update-addons",
            action="store_true",
            help="Only update addons without running the game"
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
        