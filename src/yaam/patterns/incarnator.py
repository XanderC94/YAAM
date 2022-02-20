'''
Game model incarnator module
'''
from abc import ABC, abstractmethod
from typing import TypeVar, Generic


P0 = TypeVar('P0')
P1 = TypeVar('P1')
IncOut = TypeVar('IncOut')


class Incarnator(ABC, Generic[P0, IncOut]):
    '''
    Incarnator pattern interface
    '''

    @abstractmethod
    def incarnate(self, param: P0 = None) -> IncOut:
        '''
        Return the object incarnation
        '''
        return None


class BiIncarnator(ABC, Generic[P0, P1, IncOut]):
    '''
    Double Incarnator pattern interface
    '''

    @abstractmethod
    def incarnate(self, param0: P0 = None, param1: P1 = None) -> IncOut:
        '''
        Return the object incarnation
        '''
        return None


class StaticIncarnator(ABC, Generic[P0, IncOut]):
    '''
    Static Incarnator pattern interface
    '''

    @staticmethod
    @abstractmethod
    def incarnate(param: P0 = None) -> IncOut:
        '''
        Return the object incarnation
        '''
        return None


class StaticBiIncarnator(ABC, Generic[P0, P1, IncOut]):
    '''
    Static Double Incarnator pattern interface
    '''

    @staticmethod
    @abstractmethod
    def incarnate(param0: P0 = None, param1: P1 = None) -> IncOut:
        '''
        Return the object incarnation
        '''
        return None
