'''
Yaam command line options module
'''
from enum import Enum
from typing import Any, Set

class Option(Enum):
    '''
    Yaam command line options
    '''
    UPDATE_ADDONS = (0, set(["update-addons", "update_addons"]), False)

    def __hash__(self) -> int:
        return hash(tuple([self.index, *[ _ for _ in self.aliases ], self.default]))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Option):
            return self.index == o.index
        else:
            return False

    @property
    def aliases(self) -> Set[str]:
        '''
        Return option aliases
        '''
        return self.value[1]

    @property
    def index(self) -> tuple:
        '''
        return option index
        '''
        return super().value[0]

    @property
    def default(self) -> Any:
        '''
        Return default option value
        '''
        return super().value[2]

    @staticmethod
    def from_string(str_repr: str):
        '''
        Return the enum representation of the string
        '''
        obj = None

        for _ in Option:
            if str_repr == _.name or str_repr in _.aliases:
                obj = _
                break
        
        return obj
        