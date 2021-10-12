'''
Abstract Game Incarnation model class
'''

from pathlib import Path
from typing import List, Any
from abc import abstractmethod

from yaam.model.binding_type import BindingType
from yaam.model.immutable.binding import Binding
from yaam.model.immutable.addon_base import AddonBase
from yaam.model.immutable.argument import Argument, ArgumentIncarnation
from yaam.model.mutable.binding import MutableBinding
from yaam.model.mutable.addon import MutableAddon
from yaam.model.game.base import IGame
from yaam.model.game.abstract import AbstractGameBase

class IGameIncarnation(AbstractGameBase[MutableAddon, ArgumentIncarnation[Any], MutableBinding]):
    '''
    Game incarnation model interface
    '''

    @property
    @abstractmethod
    def game(self) -> IGame[AddonBase, Argument, Binding]:
        '''
        Return the underlying game of this incarnation
        '''
        return None

class AbstractGameIncarnation(IGameIncarnation):
    '''
    Abstract Game Incarnation model class
    '''

    def __init__(self, game: IGame[AddonBase, Argument, Binding]):

        super().__init__(game.binding)
        self._game = game

        self._config_path = Path()

        self._chainloads : List[List[str]] = list()

    @property
    def game(self) -> IGame[AddonBase, Argument, Binding]:
        return self._game

    @property
    def name(self):
        return self._game.name

    @property
    def config_path(self) -> Path:
        '''
        Returns the current settings path for the game.
        That is the addons, arguments and chainloads settings.
        '''
        return self._config_path

    @property
    def root(self) -> Path:
        return self._game.root

    @property
    def path(self) -> Path:
        return self._game.path

    @property
    def bin_directory(self) -> Path:
        return self._game.bin_directory

    @property
    def binding(self) -> BindingType:
        return self._binding_type

    @property
    def chains(self) -> List[List[str]]:
        '''
        Returns game chainloads
        '''
        return self._chainloads

    @abstractmethod
    def load(self) -> bool:
        '''
        Loads the current settings for the game.
        '''
        return False
