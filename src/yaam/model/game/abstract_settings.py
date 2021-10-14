'''
Abstract Game class module
'''

from pathlib import Path
from typing import Dict, Set, List, TypeVar, Union
from yaam.model.binding_type import BindingType
from yaam.model.game.settings import IYaamGameSettings

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
D = TypeVar('D')

class AbstractYaamGameSettings(IYaamGameSettings[A, B, C, D], object):
    '''
    Abstract Yaam Game Settings model class
    '''

    def __init__(self, settings_path: Path, binding : BindingType = BindingType.AGNOSTIC):

        self._settings_path = settings_path
        
        self._args : Set[C] = set()
        self._bases : Dict[str, D] = list()
        self._addons : List[A] = list()
        self._bindings : Dict[BindingType, Dict[str, B]] = dict()
        self._chains : List[List[str]] = list()
        self._binding_type : BindingType = binding
    
    @property
    def path(self) -> Path:
        return self._settings_path

    @property
    def binding(self) -> BindingType:
        return self._binding_type

    def set_binding(self, new_binding: BindingType):
        self._binding_type = new_binding

    @property
    def bindings(self) -> Dict[BindingType, Dict[str, B]]:
        return self._bindings

    @property
    def bases(self) -> Dict[str, D]:
        return self._bases

    @property
    def arguments(self) -> Set[A]:
        return self._args

    @property
    def addons(self) -> List[A]:
        return self._addons

    @property
    def chains(self) -> List[List[str]]:
        return self._chains

    def has_addon(self, obj: Union[str, A]) -> bool:
        return obj in self._addons

    def has_argument(self, obj: Union[str, C]) -> bool:
        return obj in self._args

    def addon(self, name: str) -> A:
        return next((_ for _ in self._addons if name == _.name), None)

    def argument(self, name: str) -> C:
        return next((_ for _ in self._args if name == _), None)

    def add_addon(self, addon: A) -> bool:
        ret = not self.has_addon(addon)

        if ret:
            self._addons.append(addon)

        return ret

    def add_argument(self, arg: C) -> bool:

        ret = not self.has_argument(arg)

        if ret:
            self._args.add(arg)

        return ret

    def remove(self, addon: A) -> bool:
        ret = addon in self._addons

        if ret:
            self._addons.remove(addon.name)

        return ret
