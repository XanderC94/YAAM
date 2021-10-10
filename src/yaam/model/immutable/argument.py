'''
Command line argument module
'''
from typing import TypeVar, Generic, Any
from yaam.model.incarnator import Incarnator
from yaam.model.argument_type import ArgumentType

T = TypeVar('T')

class ArgumentIncarnation(Generic[T], object):
    '''
    Immutable command line argument incarnation class
    '''

    def __init__(self, name: str, value: T = None):
        self._name = name
        self._value = value

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, o: object) -> bool:

        if isinstance(o, ArgumentIncarnation):
            return self.__hash__() == o.__hash__()
        elif isinstance(o, str):
            return self.name == o or self.name == o[1:]

        return super().__eq__(o)

    @property
    def name(self) ->str:
        '''
        Argument name
        '''
        return self._name

    @property
    def value(self) -> T:
        '''
        Argument value
        '''
        return self._value

    @value.setter
    def value(self, value : T):
        '''
        Set argument value
        '''
        self._value = value

    def __str__(self) -> str:
        return f"-{self._name} {self._value}" if self._value else f"-{self._name}"

    @staticmethod
    def from_string(json_str: str):
        '''
        Create argument incarnation representation from a string
        '''
        tokens = json_str[1:].split(" ")
        return ArgumentIncarnation(*tokens)

class Argument(Incarnator[Any, ArgumentIncarnation[Any]], object):
    '''
    Immutable Command line Argument class
    '''

    def __init__(self, name: str, values: list, value_type = ArgumentType.NONE,
            descr = str(), deprecated = False, user_defined=False) -> None:

        self._name = name
        self._values = values
        self._value_type = value_type
        self._descr = descr
        self._deprecated = deprecated
        self._user_defined = user_defined

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, o: object) -> bool:

        if isinstance(o, ArgumentIncarnation):
            return self.__hash__() == o.__hash__()
        elif isinstance(o, str):
            return self.name == o or self.name == o[1:]
            
        return super().__eq__(o)

    @property
    def name(self) -> str():
        '''
        Return the argument name
        '''
        return self._name

    @property
    def values(self) -> list():
        '''
        Return the argument values
        '''
        return self._values

    @property
    def typing(self) -> ArgumentType:
        '''
        Return the argument type
        '''
        return self._value_type

    @property
    def descr(self):
        '''
        Return the argument description
        '''
        return self._descr

    @property
    def is_deprecated(self):
        '''
        Return if whether the argument is deprecated or temporaly disable
        '''
        return self._deprecated

    @property
    def is_user_defined(self):
        '''
        Return whether the argument values are user defined
        '''
        return self._user_defined

    def incarnate(self, decoration: Any = None) -> ArgumentIncarnation[Any]:
        '''
        Create an incarnation of this command line argument
        '''
        return ArgumentIncarnation(self._name, decoration)

    @staticmethod
    def from_dict(json_obj: dict):
        '''
        Create argument incarnation representation from a string
        '''
        name = json_obj["name"]
        values = json_obj["values"] if "values" in json_obj else []
        value_type = (
            ArgumentType.from_string(json_obj["value_type"])
            if "value_type" in json_obj else ArgumentType.BOOLEAN
        )
        deprecated = json_obj["deprecated"] if "deprecated" in json_obj else False
        user_defined = json_obj["user_defined"] if "user_defined" in json_obj else len(values) == 0

        return Argument(name, values, value_type, deprecated, user_defined)
