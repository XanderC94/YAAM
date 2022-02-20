'''
Game static incarnator module
'''
from abc import abstractmethod
from yaam.model.game.contract.base import IGame
from yaam.patterns.incarnator import StaticBiIncarnator
from yaam.model.appcontext import AppContext

from yaam.model.mutable.addon_base import AddonBase
from yaam.model.mutable.binding import Binding


class IGameIncarnator(StaticBiIncarnator[str, AppContext, IGame[AddonBase, Binding]]):
    '''
    Game class static incarnator trait
    '''

    @staticmethod
    @abstractmethod
    def incarnate(game_name: str, app_context: AppContext = None) -> IGame[AddonBase, Binding]:
        '''
        Create an incarnation of the game
        '''
        return None
