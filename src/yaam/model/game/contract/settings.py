'''
Game model abstract class module
'''

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Generic, TypeVar, Union, ValuesView
from yaam.model.type.binding import BindingType

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
D = TypeVar('D')

class IYaamGameSettings(ABC, Generic[A, B, C, D]):
    '''
    Game yaam settings model interface
    '''

    @property
    @abstractmethod
    def path(self) -> Path:
        '''
        Returns the current settings path for the game.
        That is the addons, arguments and chainloads settings.
        '''
        return None

    @property
    @abstractmethod
    def binding(self) -> BindingType:
        '''
        Returns the game selected binding type
        '''
        return None

    @abstractmethod
    def set_binding(self, new_binding: BindingType):
        '''
        Set a new binding type for the game
        '''

    # @property
    # @abstractmethod
    # def bindings(self) -> Dict[BindingType, Dict[str, B]]:
    #     '''
    #     Returns game arguments
    #     '''
    #     return None

    # @property
    # @abstractmethod
    # def bases(self) -> Dict[str, D]:
    #     '''
    #     Returns game basis
    #     '''
    #     return None

    @property
    @abstractmethod
    def arguments(self) -> ValuesView[C]:
        '''
        Returns game arguments
        '''
        return None

    @property
    @abstractmethod
    def addons(self) -> List[A]:
        '''
        Returns game addons
        '''
        return None

    @property
    @abstractmethod
    def chains(self) -> List[List[str]]:
        '''
        Returns all the chainload sequences
        '''
        return None

    @abstractmethod
    def addon(self, name: str) -> A:
        '''
        Returns a game addon
        '''
        return None

    @abstractmethod
    def argument(self, name: str) -> A:
        '''
        Returns a game argument
        '''
        return None

    @abstractmethod
    def has_addon(self, obj: Union[str, A]) -> bool:
        '''
        Returns if the game has the requested addon
        '''
        return False

    @abstractmethod
    def has_argument(self, name: str) -> bool:
        '''
        Returns if the game has the requested argument
        '''
        return False

    @abstractmethod
    def add_addon(self, addon: A) -> bool:
        '''
        Add a new game addon
        '''
        return False

    @abstractmethod
    def add_argument(self, arg: C) -> bool:
        '''
        Add a new game argument
        '''
        return False

    @abstractmethod
    def remove(self, addon: A) -> bool:
        '''
        Remove a game addon
        '''
        return False

    @abstractmethod
    def load(self) -> bool:
        '''
        Loads the yaam game settings
        '''
        return False

    @abstractmethod
    def save(self) -> bool:
        '''
        Save the yaam game settings
        '''
        return False
