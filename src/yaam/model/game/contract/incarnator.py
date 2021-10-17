'''
Game static incarnator module 
'''
from abc import abstractmethod
from yaam.model.game.base import Game
from yaam.patterns.incarnator import StaticIncarnator
from yaam.model.context import AppContext

class IGameIncarnator(StaticIncarnator[AppContext, Game]):
    '''
    Game class static incarnator trait
    '''

    @staticmethod
    @abstractmethod
    def incarnate(app_context: AppContext = None) -> Game:
        '''
        Create an incarnation of the game
        '''
        return None
    