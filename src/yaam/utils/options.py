'''
Yaam command line options module
'''
from enum import Enum
from typing import Set

class Option(Enum):
    '''
    Yaam command line options
    '''
    UPDATE_ADDONS = (0, set(["update-addons"]))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Option):
            return self.index == o.index
        else:
            return False

    @property
    def aliases(self) -> Set[str]:
        return self.value[1]

    @property
    def index(self) -> tuple:
        return super().value[0]

