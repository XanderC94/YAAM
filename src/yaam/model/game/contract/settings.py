'''
Game model abstract class module
'''

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Generic, TypeVar, ValuesView
from yaam.model.mutable.addon import IAddon
from yaam.model.type.binding import BindingType
from yaam.patterns.synthetizer import Synthetizer


A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class BiGeneric(ABC, Generic[A, B]):
    '''
    2-generic class
    '''
    pass


class TriGeneric(ABC, Generic[A, B, C]):
    '''
    3-generic class
    '''
    pass


class IAddonSynthetizer(BiGeneric[A, B], Synthetizer[List[IAddon[A, B]]]):
    '''
    Addon synthetizer stub interface
    '''
    pass


class IYaamGameSettings(TriGeneric[A, B, C], IAddonSynthetizer[A, B]):
    '''
    Game yaam settings model interface
    '''

    @property
    @abstractmethod
    def path(self) -> Path:
        '''
        Returns the current settings dir path for the game.
        '''
        return None

    @property
    @abstractmethod
    def binding_type(self) -> BindingType:
        '''
        Returns the game selected binding type
        '''
        return None

    @abstractmethod
    def set_binding_type(self, new_binding: BindingType):
        '''
        Set a new binding type for the game
        '''
        pass

    @property
    @abstractmethod
    def bindings(self) -> Dict[BindingType, Dict[str, B]]:
        '''
        Returns game arguments
        '''
        return None

    @property
    @abstractmethod
    def bases(self) -> Dict[str, A]:
        '''
        Returns game addon basis
        '''
        return None

    @property
    @abstractmethod
    def arguments(self) -> ValuesView[C]:
        '''
        Returns game arguments
        '''
        return None

    @abstractmethod
    def addon_base(self, name: str) -> A:
        '''
        Returns a game addon_base
        '''
        return None

    @abstractmethod
    def addon_binding(self, name: str, btype: BindingType) -> A:
        '''
        Returns a game addon_base
        '''
        return None

    @abstractmethod
    def argument(self, name: str) -> C:
        '''
        Returns a game argument
        '''
        return None

    @abstractmethod
    def has_addon_base(self, objname: str) -> bool:
        '''
        Returns if the game has the requested addon
        '''
        return False

    @abstractmethod
    def has_addon_binding(self, objname: str, btype: BindingType) -> bool:
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
    def add_addon_base(self, base: A) -> bool:
        '''
        Add a new game addon base
        '''
        return False

    @abstractmethod
    def add_addon_binding(self, binding: B) -> bool:
        '''
        Add a new game addon binding
        '''
        return False

    @abstractmethod
    def add_argument(self, arg: C) -> bool:
        '''
        Add a new game argument
        '''
        return False

    @abstractmethod
    def remove_base(self, objname: str) -> bool:
        '''
        Remove a game addon base
        '''
        return False

    @abstractmethod
    def remove_binding(self, objname: str, btype: BindingType = None) -> bool:
        '''
        Remove a game addon binding
        '''
        return False

    @property
    @abstractmethod
    def namings(self) -> Dict[BindingType, Dict[str, Dict[str, str]]]:
        '''
        Return addons naming mapping
        '''
        return dict()

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

    @abstractmethod
    def digest(self) -> str:
        '''
        Return the setting digest
        '''
        return str()
