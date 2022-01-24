'''
Object synthetizer pattern module
'''
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

V = TypeVar('V')


class Synthetizer(ABC, Generic[V]):
    '''
    Synthetizer pattern interface
    '''

    @abstractmethod
    def synthetize(self) -> V:
        '''
        Return the object syntetization
        '''
        return None
