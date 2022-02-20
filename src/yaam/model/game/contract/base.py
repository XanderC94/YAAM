'''
Game interface module
'''

from abc import abstractmethod
from typing import TypeVar
from yaam.model.appcontext import GameContext
from yaam.model.game.contract.config import IGameConfiguration
from yaam.model.game.contract.settings import IYaamGameSettings, IAddonSynthetizer
from yaam.model.mutable.argument import Argument

A = TypeVar('A')
B = TypeVar('B')


class IGame(IAddonSynthetizer[A, B]):
    '''
    Game class trait
    '''

    @property
    @abstractmethod
    def context(self) -> GameContext:
        '''
        Return the current game context
        '''
        return None

    @property
    @abstractmethod
    def config(self) -> IGameConfiguration:
        '''
        Return the game configuration
        '''
        return None

    @property
    @abstractmethod
    def settings(self) -> IYaamGameSettings[A, B, Argument]:
        '''
        Return yaam's game setting
        '''
        return None
