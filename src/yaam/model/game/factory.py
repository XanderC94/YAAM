'''
Game factory module
'''

from yaam.model.appcontext import AppContext
from yaam.model.game.base import Game
from yaam.model.game.generic.base import GenericGame
from yaam.model.game.custom.gw2.base import GuildWars2


class GameFactory(object):
    '''
    A static game factory class
    '''

    @staticmethod
    def __simplify_name(game_name: str) -> str:
        return game_name.lower().strip(' \t\n\r').replace(' ', '').replace('_', '')

    @staticmethod
    def make(game_name: str, app_context: AppContext) -> Game:
        '''
        Make a game based on it's name.
        NOTE: it will resolve "special" game which
        have ad-hoc strategies / optimizations
        '''
        game: Game = None

        if game_name is not None:
            target = GameFactory.__simplify_name(game_name)

            if target == "guildwars2" or target == "gw2":
                game = GuildWars2.incarnate(game_name, app_context)
            else:
                game = GenericGame.incarnate(game_name, app_context)

        return game
