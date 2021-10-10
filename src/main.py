'''
YAAM main module
'''

from os import getenv as env
from sys import exit as close, exc_info
import traceback
from pathlib import Path
from collections import defaultdict
from tabulate import tabulate
from yaam.controller.update import update_addons
from yaam.controller.manage import restore_dll_addons, disable_dll_addons
from yaam.utils.process import run
from yaam.utils.options import Option
from yaam.utils.logger import static_logger

from yaam.model.game.gw2 import GuildWars2Incarnator as GameIncarnator
from yaam.model.game.gw2 import GuildWars2Incarnation as GameIncarnation
from yaam.utils.exceptions import ConfigLoadException

#####################################################################

def run_main():
    '''
    Main thread
    '''
    logger = static_logger()

    game : GameIncarnation = None

    try:
        game = GameIncarnator().incarnate(Path(env("APPDATA")))

        data = defaultdict(list)
        for addon in sorted(game.addons, key=lambda x: x.name):
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
    except Exception as _:

        logger.info(msg=str(_))
        # Get current system exception
        ex_type, ex_value, ex_traceback = exc_info()

        # Extract unformatter stack traces as tuples
        trace_back = traceback.extract_tb(ex_traceback)

        # Format stacktrace
        stack_trace = list()

        for trace in trace_back:
            stack_trace.append(f"File : {trace[0]} , Line : {trace[1]}, Func.Name : {trace[2]}, Message : {trace[3]}")

        logger.info(msg=f"Exception type : {ex_type.__name__} ")
        logger.info(msg=f"Exception message : {ex_value}")
        logger.info(msg=f"Stack trace : {stack_trace}")
        
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

    return game is not None

if __name__ == "__main__":

    execution_result = run_main()

    close(execution_result)
