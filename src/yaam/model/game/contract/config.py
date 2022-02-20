'''
Game model abstract class module
'''

from pathlib import Path
from abc import abstractmethod
from yaam.model.type.binding import BindingType


class IGameConfiguration(object):
    '''
    Game configuration model interface
    '''

    @property
    def name(self) -> str:
        '''
        Return the game name
        '''
        return type(self).__name__

    @property
    @abstractmethod
    def path(self) -> Path:
        '''
        Returns the game configuration path. That is the in-game configuration.
        '''
        return Path()

    @property
    @abstractmethod
    def game_root(self) -> Path:
        '''
        Returns the game root directory.
        '''
        return Path()

    @property
    @abstractmethod
    def game_path(self) -> Path:
        '''
        Returns the game executable path.
        '''
        return Path()

    @property
    @abstractmethod
    def native_binding(self) -> BindingType:
        '''
        Returns the game native binding type
        '''
        return BindingType.AGNOSTIC

    @property
    @abstractmethod
    def bin_directory(self) -> Path:
        '''
        Returns the game binaries directory.
        '''
        return Path()

    @abstractmethod
    def load(self, init_file_path: Path = None) -> bool:
        '''
        Loads the game configuration settings.
        '''
        return False
