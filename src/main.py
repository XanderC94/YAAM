'''
YAAM main module
'''

import sys
import time
from collections import defaultdict
from tabulate import tabulate
from yaam.controller.update import update_addons
from yaam.controller.manage import restore_dll_addons, disable_dll_addons
from yaam.model.game.base import Game
from yaam.utils.process import run
from yaam.model.options import Option
from yaam.utils.logger import static_logger

from yaam.model.game.gw2 import GuildWars2
from yaam.utils.exceptions import ConfigLoadException
from yaam.model.context import AppContext

#####################################################################

def run_main(app_context : AppContext):
    '''
    Main thread
    '''
    logger = static_logger()

    game : Game = None

    try:
        game = GuildWars2.incarnate(app_context)
    except ConfigLoadException as ex:
        logger.info(
            msg = f"Configuration loading error. \
            Assert that the configuration {ex.config_path} exists. \
            Remember to run the game at least once in order to generate the configuration."
        )
    finally:
        if game:
            is_addon_update_only = app_context.config.get_property(Option.UPDATE_ADDONS)

            start = time.time()
            addons_synthesis = game.synthetize()
            end = time.time()
            logger.debug(msg=f"Addon synthesis lasted {end-start} seconds.")

            data = defaultdict(list)
            for addon in sorted(addons_synthesis, key=lambda x: x.base.name):
                table = addon.to_table()
                for (key, value) in table.items():
                    data[key].append(value)

            if len(data):
                logger.info(msg="Loaded addons: ")
                table = tabulate(data, headers="keys", tablefmt='rst', colalign=("left",))
                logger.info(msg=f"\n{table}\n")

            disable_dll_addons(addons_synthesis)
            restore_dll_addons(addons_synthesis)

            update_addons(addons_synthesis)

            if not is_addon_update_only:
                run(
                    game.config.game_path,
                    game.config.game_root,
                    [str(_.synthetize()) for _ in game.settings.arguments if not _.meta.deprecated and _.enabled]
                )

                for addon in addons_synthesis:
                    if addon.binding.enabled and addon.binding.is_exe():
                        run(addon.binding.path, addon.binding.path.parent)

            logger.info(msg="Stack complete. Closing...")

    return game is not None

if __name__ == "__main__":

    app_context = AppContext()

    app_context.create_app_environment()

    execution_result = run_main(app_context)

    sys.exit(execution_result)
