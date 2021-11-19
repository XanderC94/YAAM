'''
Command line argument module
'''
from dataclasses import dataclass, field
from typing import TypeVar, Generic
from yaam.model.type.argument import ArgumentType
from yaam.utils.json.jsonkin import Jsonkin
from yaam.utils.json.repr import jsonrepr

T = TypeVar('T')

@dataclass(frozen=True)
class ArgumentSynthesis(Generic[T], Jsonkin):
    '''
    Immutable command line argument synthetis class
    '''
    _name          : str    = field(init=True)
    _value         : T      = field(init=True, default=None)

    def __hash__(self) -> int:
        return hash((self._name, self._value))

    def __eq__(self, o: object) -> bool:

        if isinstance(o, ArgumentInfo):
            return hash(self) == hash(o)
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

    @staticmethod
    def from_json(json_obj: dict):
        '''
        Create argument incarnation representation from a string
        '''
        return ArgumentSynthesis(
            json_obj.get('name', ''),
            json_obj.get('value', None)
        )

    def to_json(self) -> dict:
        arg = { 'name': self.name }

        if self.value is not None:
            arg['value'] = jsonrepr(self.value)

        return arg

@dataclass(frozen=True)
class ArgumentInfo(Jsonkin):
    '''
    Immutable Command line Argument class
    '''
    _name          : str            = field(init=True)
    _values        : list           = field(init=True)
    _value_type    : ArgumentType   = field(init=True)
    _description         : str            = field(init=True)
    _deprecated    : bool           = field(init=True)
    _user_defined  : bool           = field(init=True)

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, o: object) -> bool:

        if isinstance(o, ArgumentSynthesis):
            return hash(self) == hash(o)
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
    def description(self):
        '''
        Return the argument description
        '''
        return self._description

    @property
    def deprecated(self):
        '''
        Return if whether the argument is deprecated or temporaly disable
        '''
        return self._deprecated

    @property
    def user_defined(self):
        '''
        Return whether the argument values are user defined
        '''
        return self._user_defined

    @staticmethod
    def from_json(json_obj: dict):
        '''
        Create argument incarnation representation from a string
        '''
        name = json_obj["name"]
        values = json_obj.get("values", [])
        value_type = ArgumentType.from_string(json_obj.get("value_type", "boolean"))
        description = json_obj.get("description", "")
        deprecated = json_obj.get("deprecated", False)
        user_defined = json_obj.get("user_defined", len(values) == 0)

        return ArgumentInfo(name, values, value_type, description, deprecated, user_defined)

    def to_json(self) -> dict:
        return {
            'name': self.name,
            'values': jsonrepr(self.values),
            'value_type': self.typing.name,
            'description': self.description,
            'deprecated': self.deprecated,
            'user_defined': self.user_defined
        }
