'''
Argument typing module
'''
from enum import Enum
from typing import Any
from pathlib import Path


class ArgumentType(Enum):
    '''
    Argument value type factory
    '''
    NONE = (0, lambda x: x)
    BOOLEAN = (1, bool)
    NUMERIC = (2, float)
    IP = (3, str)
    PATH = (4, Path)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, ArgumentType):
            return self.index == o.index
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.value)

    @property
    def typing(self) -> object:
        '''
        Returns the type factory lambda
        '''
        return self.value[1]

    @property
    def index(self) -> tuple:
        '''
        Returns the numerical enum value
        '''
        return self.value[0]

    @staticmethod
    def from_string(string_repr: str):
        '''
        Return the enum representation of the string, if exists
        '''
        enum_repr = ArgumentType.NONE

        for arg_type in ArgumentType:
            if string_repr.lower() == str(arg_type).lower():
                enum_repr = arg_type
                break

        return enum_repr

    def reify(self, value: Any):
        '''
        Return the value real representation
        '''
        return self.typing(value)
