'''
Game model incarnator module
'''
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

V = TypeVar('V')
I = TypeVar('I')

class Incarnator(ABC, Generic[V, I]):
    '''
    Base incarnator model.
    '''

    @abstractmethod
    def incarnate(self, decoration: V = None) -> I:
        '''
        Return the object incarnation
        '''
        return None
