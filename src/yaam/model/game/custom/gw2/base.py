'''
Guild Wars 2 model class
'''
from yaam.model.game.custom.gw2.config import GW2Config
from yaam.model.game.custom.gw2.settings import YaamGW2Settings
from yaam.utils.exceptions import ConfigLoadException
from yaam.model.game.contract.config import IGameConfiguration
from yaam.model.game.contract.incarnator import IGameIncarnator
from yaam.model.game.contract.settings import IYaamGameSettings
from yaam.model.game.base import Game
from yaam.model.appcontext import AppContext, GameContext

class GuildWars2(Game, IGameIncarnator):
    '''
    Guild Wars 2 model class incarnator
    '''
    def __init__(self, config: IGameConfiguration, settings: IYaamGameSettings, game_context: GameContext) -> None:
        Game.__init__(self, config, settings, game_context)

    @staticmethod
    def incarnate(game_name: str = "Guild Wars 2", app_context: AppContext = None) -> Game:
        gw2_config = GW2Config(app_context.appdata_dir)

        init_file_path = app_context.init_file_path(game_name)

        if not gw2_config.load(init_file_path):
            raise ConfigLoadException(
                gw2_config.path,
                msg = (
                    "Configuration loading error. "
                    + f"Assert that the configuration {gw2_config.path} exists. "
                    + "Remember to run the game at least once in order to generate the configuration."
                )
            )

        game_context = app_context.create_game_environment(gw2_config.name, gw2_config.game_root)

        yaam_gw2_settings = YaamGW2Settings(game_context, gw2_config.native_binding)
        yaam_gw2_settings.load()

        return GuildWars2(gw2_config, yaam_gw2_settings, game_context)
