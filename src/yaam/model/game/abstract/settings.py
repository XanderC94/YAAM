'''
Abstract Game class module
'''

from pathlib import Path
from typing import Dict, TypeVar, ValuesView
from yaam.model.type.binding import BindingType
from yaam.model.game.contract.settings import IYaamGameSettings

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
D = TypeVar('D')


class AbstractYaamGameSettings(IYaamGameSettings[A, B, C, D], object):
    '''
    Abstract Yaam Game Settings model class
    '''

    def __init__(self, settings_path: Path, binding: BindingType = BindingType.AGNOSTIC):

        self._settings_path = settings_path

        self._args: Dict[str, C] = dict()
        self._bases: Dict[str, D] = dict()
        self._bindings: Dict[BindingType, Dict[str, B]] = dict()
        self._binding_type: BindingType = binding
        self._naming_map: Dict[BindingType, Dict[str, Dict[str, str]]] = dict()

    @property
    def path(self) -> Path:
        return self._settings_path

    @property
    def binding_type(self) -> BindingType:
        return self._binding_type

    def set_binding_type(self, new_binding: BindingType):
        self._binding_type = new_binding

    @property
    def bindings(self) -> Dict[BindingType, Dict[str, B]]:
        return self._bindings

    @property
    def bases(self) -> Dict[str, D]:
        return self._bases

    @property
    def arguments(self) -> ValuesView[C]:
        return self._args.values()

    def has_addon_base(self, objname: str) -> bool:
        return objname in self._bases

    def has_addon_binding(self, objname: str, btype: BindingType) -> bool:
        return btype in self._bindings and objname in self._bindings[btype]

    def has_argument(self, name: str) -> bool:
        return name in self._args

    def addon_base(self, name: str) -> A:
        return self._bases.get(name, None)

    def addon_binding(self, name: str, btype: BindingType) -> A:
        return self._bindings.get(btype, dict()).get(name, None)

    def argument(self, name: str) -> C:
        return self._args.get(name, None)

    def add_argument(self, arg: C) -> bool:

        ret = not self.has_argument(arg)

        if ret:
            self._args[str(arg)] = arg

        return ret

    def remove_base(self, objname: str) -> bool:
        ret = objname in self._bases

        if ret:
            self._bases.pop(objname)
            for key in self._bindings:
                if objname in self._bindings[key]:
                    self._bindings[key].pop(objname)

        return ret

    def remove_binding(self, objname: str, btype: BindingType = None) -> bool:
        ret = False

        if btype is None:
            for key in self._bindings:
                if objname in self._bindings[key]:
                    self._bindings[key].pop(objname)
                    ret = True

        elif btype in self._bindings and objname in self._bindings[btype]:
            self._bindings[btype].pop(objname)
            ret = True

        return ret

    @property
    def namings(self) -> Dict[BindingType, Dict[str, Dict[str, str]]]:
        return self._naming_map
