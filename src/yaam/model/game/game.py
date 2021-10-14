'''
'''
from abc import abstractmethod
from yaam.model.incarnator import Incarnator
from yaam.model.game.config import IGameConfiguration
from yaam.model.game.settings import IYaamGameSettings
from yaam.model.context import ApplicationContext

class Game(object):
    '''
    Game class trait
    '''
    def __init__(self, config: IGameConfiguration, settings: IYaamGameSettings) -> None:
        self._config = config
        self._yaam_settings = settings

    @property
    def config(self) -> IGameConfiguration:
        '''
        Return the game configuration
        '''
        return self._config

    @property
    def settings(self) -> IYaamGameSettings:
        '''
        Return the yaam's game setting
        '''
        return self._yaam_settings

class IGameIncarnator(Incarnator[ApplicationContext, Game]):
    '''
    Game class incarnator
    '''

    @abstractmethod
    def incarnate(self, app_context: ApplicationContext = None) -> Game:
        return None
