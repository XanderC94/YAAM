'''
Generic game class module
'''

from yaam.model.appcontext import AppContext, GameContext
from yaam.model.game.base import Game
from yaam.model.game.contract.incarnator import IGameIncarnator
from yaam.model.game.contract.config import IGameConfiguration
from yaam.model.game.contract.settings import IYaamGameSettings
from yaam.model.game.generic.config import GenericGameConfig
from yaam.model.game.generic.settings import GenericYaamGameSettings
from yaam.utils.exceptions import ConfigLoadException


class GenericGame(Game, IGameIncarnator):
    '''
    Guild Wars 2 model class incarnator
    '''
    def __init__(self, config: IGameConfiguration, settings: IYaamGameSettings, game_context: GameContext) -> None:
        Game.__init__(self, config, settings, game_context)

    @staticmethod
    def incarnate(game_name: str, app_context: AppContext = None) -> Game:
        config = GenericGameConfig(app_context.appdata_dir)

        init_file_path = app_context.init_file_path(game_name)

        if not config.load(init_file_path):
            raise ConfigLoadException(
                config.path, msg=f"Configuration loading error. {config.path} might not exists."
            )

        game_context = app_context.create_game_environment(config.name, config.game_root)

        yaam_settings = GenericYaamGameSettings(game_context, config.native_binding)
        yaam_settings.load()

        return GenericGame(config, yaam_settings, game_context)
