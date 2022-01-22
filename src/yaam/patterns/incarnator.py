'''
Game model incarnator module
'''
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

V = TypeVar('V')
N = TypeVar('N')
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

class BiIncarnator(ABC, Generic[N, V, I]):
    '''
    Double Incarnator pattern interface
    '''

    @abstractmethod
    def incarnate(self, value1 : N, value2: V = None) -> I:
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

class StaticBiIncarnator(ABC, Generic[N, V, I]):
    '''
    Static Double Incarnator pattern interface
    '''

    @staticmethod
    @abstractmethod
    def incarnate(value1 : N, value2: V = None) -> I:
        '''
        Return the object incarnation
        '''
        return None
