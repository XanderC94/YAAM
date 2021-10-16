'''
Command line argument module
'''
from dataclasses import dataclass, field
from typing import TypeVar, Generic
from yaam.model.argument_type import ArgumentType

T = TypeVar('T')

@dataclass(frozen=True)
class ArgumentSynthesis(Generic[T], object):
    '''
    Immutable command line argument synthetis class
    '''
    _name          : str    = field(init=True)
    _value         : T      = field(init=True, default=None)

    # def __init__(self, name: str, value: T = None):
    #     self._name = name
    #     self._value = value

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, o: object) -> bool:

        if isinstance(o, Argument):
            return self.__hash__() == o.__hash__()
        elif isinstance(o, str):
            return self.name == o or self.name == o[1:]
        return super().__eq__(o)

    def __str__(self) -> str:
        return (
            f"-{self._name} {self._value}"
            if self._value is not None
            else f"-{self._name}"
        )

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

    @staticmethod
    def from_string(json_str: str):
        '''
        Create argument incarnation representation from a string
        '''
        tokens = json_str[1:].split(" ")
        return ArgumentSynthesis(*tokens)

@dataclass(frozen=True)
class Argument(object):
    '''
    Immutable Command line Argument class
    '''
    _name          : str            = field(init=True)
    _values        : list           = field(init=True)
    _value_type    : ArgumentType   = field(init=True)
    _descr         : str            = field(init=True)
    _deprecated    : bool           = field(init=True)
    _user_defined  : bool           = field(init=True)

    # def __init__(self, name: str, values: list, value_type: ArgumentType = ArgumentType.NONE,
    #         descr: str = str(), deprecated: bool = False, user_defined:bool = False) -> None:

    #     self._name = name
    #     self._values = values
    #     self._value_type = value_type
    #     self._descr = descr
    #     self._deprecated = deprecated
    #     self._user_defined = user_defined

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, o: object) -> bool:

        if isinstance(o, ArgumentSynthesis):
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

    @staticmethod
    def from_dict(json_obj: dict):
        '''
        Create argument incarnation representation from a string
        '''
        name = json_obj["name"]
        values = json_obj.get("values", [])
        value_type = ArgumentType.from_string(json_obj.get("value_type", "boolean"))
        descr = json_obj.get("description", "")
        deprecated = json_obj.get("deprecated", False)
        user_defined = json_obj.get("user_defined", len(values) == 0)

        return Argument(name, values, value_type, descr, deprecated, user_defined)
