'''
Mutable Addon module
'''
from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar
from yaam.model.mutable.binding import Binding
from yaam.model.mutable.addon_base import AddonBase


A = TypeVar('A')
B = TypeVar('B')


class IAddon(ABC, Generic[A, B]):
    '''
    Mutable Addon interface
    '''

    @property
    @abstractmethod
    def base(self) -> AddonBase:
        '''
        Return the Addon Base object
        '''
        return None

    @property
    @abstractmethod
    def binding(self) -> Binding:
        '''
        Return the Addon Binding object
        '''
        return None

    @property
    @abstractmethod
    def naming(self) -> Dict[str, str]:
        '''
        Return the Addon naming rules
        '''
        return None

    @property
    @abstractmethod
    def is_valid(self) -> bool:
        '''
        Return whether this addon has a valid configuration or not.
        Name should not be empty and the path should be an existing one.
        '''
        return False

    @abstractmethod
    def to_table(self) -> dict:
        '''
        Return a partial dict repr of the addon
        '''
        return None


class Addon(IAddon[AddonBase, Binding]):
    '''
    Mutable Addon incarnation class
    '''

    def __init__(self, base: AddonBase, binding: Binding, naming: Dict[str, str]):
        self._base = base
        self._binding = binding
        self._naming = naming

    def __hash__(self) -> int:
        return hash((self._binding.name, self._binding.typing))

    def __eq__(self, o: object) -> bool:

        if issubclass(type(o), Addon):
            return hash(self) == hash(o)
        elif issubclass(type(o), AddonBase):
            return self._base == o
        elif issubclass(type(o), Binding):
            return self._binding == o
        elif isinstance(o, str):
            return self._base.name == o

        return super().__eq__(o)

    @property
    def base(self) -> AddonBase:
        return self._base

    @property
    def binding(self) -> Binding:
        return self._binding

    @property
    def naming(self) -> Dict[str, str]:
        return self._naming

    @property
    def is_valid(self) -> bool:
        return len(self._base.name) > 0 and self._binding.path.exists()

    def to_table(self) -> dict:
        table: dict = {}

        table['name'] = self._base.name
        table['path'] = self._binding.path.name
        table['binding'] = self._binding.typing.name.lower()
        table['enabled'] = self._binding.is_enabled
        table['update'] = self._binding.is_updateable

        return table
