'''
Game static incarnator module 
'''
from abc import abstractmethod
from yaam.model.game.base import Game
from yaam.patterns.incarnator import StaticBiIncarnator
from yaam.model.appcontext import AppContext

class IGameIncarnator(StaticBiIncarnator[str, AppContext, Game]):
    '''
    Game class static incarnator trait
    '''

    @staticmethod
    @abstractmethod
    def incarnate(game_name: str, app_context: AppContext = None) -> Game:
        '''
        Create an incarnation of the game
        '''
        return None
    