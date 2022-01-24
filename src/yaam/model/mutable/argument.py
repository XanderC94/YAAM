'''
Mutable Argument module
'''

from typing import TypeVar
from yaam.model.immutable.argument import ArgumentInfo, ArgumentSynthesis
from yaam.model.type.argument import ArgumentType
from yaam.patterns.synthetizer import Synthetizer
from yaam.utils.json.jsonkin import Jsonkin
from yaam.utils.json.repr import jsonrepr

T = TypeVar('T')


class Argument(Synthetizer[ArgumentSynthesis[T]], Jsonkin):
    '''
    Mutable Argument model class
    '''

    def __init__(self, arg: ArgumentInfo, value: T = None, enabled=False):
        self.value: T = value
        self.enabled: bool = enabled
        self._argument: ArgumentInfo = arg

    def __hash__(self) -> int:
        return hash(self.meta.name)

    def __str__(self) -> str:
        return self.meta.name

    @property
    def meta(self):
        '''
        Returns underlying argument info
        '''
        return self._argument

    def synthetize(self) -> ArgumentSynthesis[T]:
        return ArgumentSynthesis(self.meta.name, self.value)

    @staticmethod
    def from_json(json_obj: dict):
        '''
        Return the object representation of this object
        '''
        enabled = json_obj.get('enabled', False)
        value = json_obj.get('value', None)
        return Argument(ArgumentInfo.from_json(json_obj), value, enabled)

    def to_json(self) -> dict:
        '''
        Map the json rapresentation into an object of this class
        '''
        arg = {'name': self.meta.name}

        if self.meta.typing is not ArgumentType.NONE:
            arg['value'] = jsonrepr(self.value)

        return arg
