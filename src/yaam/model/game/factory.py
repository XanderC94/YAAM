'''
Game factory module
'''

from yaam.model.appcontext import AppContext
from yaam.model.game.contract.base import IGame
from yaam.model.game.contract.incarnator import IGameIncarnator
from yaam.model.game.generic.base import GenericGame
from yaam.model.game.custom.gw2.base import GuildWars2
from yaam.model.mutable.addon_base import AddonBase
from yaam.model.mutable.binding import Binding


class GameFactory(IGameIncarnator):
    '''
    A static game factory class
    '''

    @staticmethod
    def __simplify_name(game_name: str) -> str:
        return game_name.lower().strip(' \t\n\r').replace(' ', '').replace('_', '')

    @staticmethod
    def incarnate(game_name: str, app_context: AppContext) -> IGame[AddonBase, Binding]:
        '''
        Make a game based on it's name.
        NOTE: it will resolve "special" game which
        have ad-hoc strategies / optimizations
        '''
        game: IGame[AddonBase, Binding] = None

        if game_name is not None:
            target = GameFactory.__simplify_name(game_name)

            if target == "guildwars2" or target == "gw2":
                game = GuildWars2.incarnate(game_name, app_context)
            else:
                game = GenericGame.incarnate(game_name, app_context)

        return game
