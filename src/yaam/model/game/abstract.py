'''
Abstract Game class module
'''

from pathlib import Path
from typing import Dict, Set, List, TypeVar, Union
from yaam.model.immutable.argument import Argument
from yaam.model.immutable.addon_base import AddonBase
from yaam.model.immutable.binding import BindingType, Binding
from yaam.model.game.base import IGame
from yaam.utils.exceptions import ConfigLoadException

C = TypeVar('C')
A = TypeVar('A')
B = TypeVar('B')

class AbstractGameBase(IGame[A, C, B], object):
    '''
    Game model base class
    '''

    def __init__(self, config_path: Path, default_binding : BindingType = BindingType.AGNOSTIC):

        self._config_path = config_path
        self._binding_type = default_binding
        self._args : Set[C] = set()
        self._addons : List[A] = list()
        self._bindings : Dict[BindingType, Dict[str, B]] = dict()

    @property
    def config_path(self) -> Path:
        return self._config_path

    @property
    def binding(self) -> BindingType:
        return self._binding_type

    # @property
    # def bindings(self) -> Dict[BindingType, Dict[str, B]]:
    #     return self._bindings

    @property
    def arguments(self) -> Set[A]:
        return self._args

    @property
    def addons(self) -> List[A]:
        return self._addons

    def has_addon(self, obj: Union[str, A]) -> bool:
        return obj in self._addons

    def has_argument(self, obj: Union[str, C]) -> bool:
        return obj in self._args

    def addon(self, name: str) -> A:
        return next((_ for _ in self._addons if name == _.name), None)

    def argument(self, name: str) -> A:
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

class AbstractGame(AbstractGameBase[AddonBase, Argument, Binding], object):
    '''
    Game model class
    '''

    def __init__(self, appdata: Path):

        super().__init__(appdata, BindingType.AGNOSTIC)

        self._app_data = appdata
        self._root = Path()
        self._exe = str()

    def __enter__(self):
        if not self.load():
            raise ConfigLoadException(self._config_path)
        return self

    def __exit__(self, *args):
        pass

    @property
    def root(self) -> Path:
        return self._root

    @property
    def path(self) -> Path:
        return self.root / self._exe

    @property
    def bin_directory(self) -> Path:
        return self.root / "bin"
