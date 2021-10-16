'''
Mutable Argument module
'''

from typing import TypeVar
from yaam.model.immutable.argument import Argument, ArgumentSynthesis
from yaam.model.synthetizer import Synthetizer

T = TypeVar('T')

class MutableArgument(Synthetizer[ArgumentSynthesis[T]], object):
    '''
    Mutable Argument model class
    '''

    def __init__(self, arg: Argument, value: T = None, enabled=False):
        self.value: T = value
        self.enabled : bool = enabled
        self._argument: Argument = arg

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
    def from_dict(json_obj:dict):
        '''
        Return the object representation of this object
        '''
        enabled = json_obj.get('enabled', False)
        value = json_obj.get('value', None)

        return MutableArgument(Argument.from_dict(json_obj), value, enabled)
        