'''
Game model abstract class module
'''

from pathlib import Path
from typing import Set, List, Generic, TypeVar, Union

from abc import ABC, abstractmethod
from yaam.model.binding_type import BindingType

C = TypeVar('C')
A = TypeVar('A')

class IGame(ABC, Generic[A, C]):
    '''
    Game model Interface
    '''

    @property
    def name(self) -> str:
        '''
        Return the game name
        '''
        return type(self).__name__

    @property
    @abstractmethod
    def config_path(self) -> Path:
        '''
        Returns the game configuration path. That is the in-game configuration.
        '''
        return Path()

    @property
    @abstractmethod
    def root(self) -> Path:
        '''
        Returns the game root directory.
        '''
        return Path()

    @property
    @abstractmethod
    def path(self) -> Path:
        '''
        Returns the game executable path.
        '''
        return Path()

    @property
    @abstractmethod
    def binding(self) -> BindingType:
        '''
        Returns the game binding type
        '''
        return BindingType.AGNOSTIC

    @property
    @abstractmethod
    def bin_directory(self) -> Path:
        '''
        Returns the game binaries directory.
        '''
        return Path()

    @property
    @abstractmethod
    def arguments(self) -> Set[C]:
        '''
        Returns game arguments
        '''
        return set()

    @property
    @abstractmethod
    def addons(self) -> List[A]:
        '''
        Returns game addons
        '''
        return dict()

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
    def has_argument(self, obj: Union[str, C]) -> bool:
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
        Loads the game configuration settings.
        '''
        return False
