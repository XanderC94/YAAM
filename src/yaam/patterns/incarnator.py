'''
Game model incarnator module
'''
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

V = TypeVar('V')
I = TypeVar('I')

class Incarnator(ABC, Generic[V, I]):
    '''
    Incarnator pattern interface
    '''

    @abstractmethod
    def incarnate(self, value: V = None) -> I:
        '''
        Return the object incarnation
        '''
        return None

class StaticIncarnator(ABC, Generic[V, I]):
    '''
    Static Incarnator pattern interface
    '''

    @staticmethod
    @abstractmethod
    def incarnate(value: V) -> I:
        '''
        Return the object incarnation
        '''
        return None
