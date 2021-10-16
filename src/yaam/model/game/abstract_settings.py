'''
Abstract Game class module
'''

from pathlib import Path
from typing import Dict, List, TypeVar, ValuesView, Union
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
        
        self._args : Dict[str, C] = dict()
        self._bases : Dict[str, D] = dict()
        self._chains : List[List[str]] = list()
        self._addons : List[A] = list()
        self._bindings : Dict[BindingType, Dict[str, B]] = dict()
        self._binding_type : BindingType = binding
    
    @property
    def path(self) -> Path:
        return self._settings_path

    @property
    def binding(self) -> BindingType:
        return self._binding_type

    def set_binding(self, new_binding: BindingType):
        self._binding_type = new_binding

    # @property
    # def bindings(self) -> Dict[BindingType, Dict[str, B]]:
    #     return self._bindings

    # @property
    # def bases(self) -> Dict[str, D]:
    #     return self._bases

    @property
    def arguments(self) -> ValuesView[C]:
        return self._args.values()

    @property
    def addons(self) -> List[A]:
        return self._addons

    @property
    def chains(self) -> List[List[str]]:
        return self._chains

    def has_addon(self, obj: Union[str, A]) -> bool:
        return obj in self._bases if isinstance(obj, str) else obj in self._addons

    def has_argument(self, name: str) -> bool:
        return name in self._args

    def addon(self, name: str) -> A:
        return next((_ for _ in self._addons if name == _.name), None)

    def argument(self, name: str) -> C:
        return self._args.get(name, None)

    def add_addon(self, addon: A) -> bool:
        ret = not self.has_addon(addon)

        if ret:
            self._addons.append(addon)

        return ret

    def add_argument(self, arg: C) -> bool:

        ret = not self.has_argument(arg)

        if ret:
            self._args[str(arg)] = arg

        return ret

    def remove(self, addon: str) -> bool:
        ret = addon in self._addons

        if ret:
            self._addons.remove(addon.name)

        return ret
