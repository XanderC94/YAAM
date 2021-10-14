'''
YAAM main module
'''

import sys
from collections import defaultdict
from tabulate import tabulate
from yaam.controller.update import update_addons
from yaam.controller.manage import restore_dll_addons, disable_dll_addons
from yaam.model.game.game import Game
from yaam.utils.process import run
from yaam.utils.options import Option
from yaam.utils.logger import static_logger

from yaam.model.game.gw2 import GuildWars2
from yaam.utils.exceptions import ConfigLoadException
from yaam.model.context import ApplicationContext

#####################################################################

def run_main(app_context : ApplicationContext):
    '''
    Main thread
    '''
    logger = static_logger()

    game : Game = None

    try:
        game = GuildWars2.incarnate(app_context)

        data = defaultdict(list)
        for addon in sorted(game.settings.addons, key=lambda x: x.base.name):
            table = addon.to_table()
            for (key, value) in table.items():
                data[key].append(value)

        if len(data):
            logger.info(msg="Loaded addons: ")
            table = tabulate(data, headers="keys", tablefmt='rst', colalign=("left",))
            logger.info(msg=f"\n{table}\n")

    except ConfigLoadException as ex:
        logger.info(
            msg = f"Configuration loading error. \
            Assert that the configuration {ex.config_path} exists. \
            Remember to run the game at least once in order to generate the configuration."
        )
    finally:
        if game:
            is_addon_update_only = sum([
                1 for _ in Option.UPDATE_ADDONS.aliases if _ in game.settings.arguments
            ]) > 0

            disable_dll_addons(game.settings.addons)
            restore_dll_addons(game.settings.addons)

            update_addons(game.settings.addons)

            if not is_addon_update_only:
                run(game.config.game_path, game.config.game_root, game.settings.arguments)

                for addon in game.settings.addons:
                    if addon.is_enabled and addon.is_exe():
                        run(addon.path, addon.path.parent)

                logger.info(msg="Stack complete. Closing...")

    return game is not None

if __name__ == "__main__":

    app_ctx = ApplicationContext()

    app_ctx.create_app_environment()

    execution_result = run_main(app_ctx)

    sys.exit(execution_result)
