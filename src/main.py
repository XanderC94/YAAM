'''
YAAM main module
'''

from os import getenv as env
from sys import exit as close, stdout
from pathlib import Path
from tabulate import tabulate

from yaam.controller.update import update_addons
from yaam.controller.manage import restore_dll_addons, disable_dll_addons
from yaam.utils.process import run
from yaam.utils.options import Option
from yaam.utils.logger import static_logger, logging

from yaam.model.game.gw2 import GuildWars2Incarnator as GameIncarnator
from yaam.model.game.gw2 import GuildWars2Incarnation as GameIncarnation
from yaam.utils.exceptions import ConfigLoadException

#####################################################################

if __name__ == "__main__":

    logger = static_logger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(stdout)
    logger.addHandler(handler)

    game : GameIncarnation = None

    try:
        game = GameIncarnator().incarnate(Path(env("APPDATA")))

        data = dict()
        for addon in sorted(game.addons, key=lambda x: x.name):
            table = addon.to_table()
            for (k, v) in table.items():
                if k not in data:
                    data[k] = list()
                data[k].append(v)

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
                1 for _ in Option.UPDATE_ADDONS.aliases if _ in game.arguments
            ]) > 0

            disable_dll_addons(game.addons)
            restore_dll_addons(game.addons)

            update_addons(game.addons)

            if not is_addon_update_only:
                run(game.path, game.root, game.arguments)

                for addon in game.addons:
                    if addon.is_enabled and addon.is_exe():
                        run(addon.path, addon.path.parent)

                logger.info(msg="Stack complete. Closing...")

    close(game is not None)
