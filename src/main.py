'''
YAAM main module
'''

import sys
from copy import deepcopy
from yaam.controller.cmd.repl import repl
from yaam.controller.update.updater import AddonUpdater
from yaam.controller.manage import restore_dll_addons, disable_dll_addons
from yaam.model.game.base import Game
from yaam.utils import process
from yaam.model.options import Option
from yaam.utils.logger import static_logger
from yaam.utils.print import print_addon_tableau
from yaam.model.game.gw2 import GuildWars2
from yaam.utils.exceptions import ConfigLoadException
from yaam.model.context import AppContext
from yaam.utils.timer import Timer

#####################################################################

def run_main(app_context : AppContext):
    '''
    Main thread
    '''
    logger = static_logger()

    game : Game = None
    game_stasis : Game = None
    try:
        game = GuildWars2.incarnate(app_context)
        game_stasis = deepcopy(game)
    except ConfigLoadException as ex:
        logger.info(
            msg = f"Configuration loading error. \
            Assert that the configuration {ex.config_path} exists. \
            Remember to run the game at least once in order to generate the configuration."
        )
    finally:
        if game:
            is_edit_mode = app_context.config.get_property(Option.EDIT)
            is_addon_update_only = app_context.config.get_property(Option.UPDATE_ADDONS)
            is_run_only = app_context.config.get_property(Option.RUN_STACK)
            is_export_only = app_context.config.get_property(Option.EXPORT)

            prev_game_binding = game_stasis.settings.binding
            prev_addons_synthesis = game_stasis.synthetize()

            print_addon_tableau(prev_addons_synthesis, lambda x: logger.info(msg=x))

            # if is_edit_mode:
            #     repl(game)

            # save addons after editing
            # only if edit has effectively made changes to the configuration
            curr_settings_digest = game.settings.digest()
            prev_settings_digest = game_stasis.settings.digest()
            logger.debug(msg=f"Current settings digest is {curr_settings_digest}.")
            logger.debug(msg=f"Previous settings digest is {prev_settings_digest}.")

            if curr_settings_digest != prev_settings_digest:
                game.settings.save()
                logger.info(msg="Settings changes have been saved.")
            else:
                logger.info(msg="No settings changes have been registered.")

            # in order to know HOW to correctly disable previous shaders and
            # enable the new ones, if any, it is necessary to know the previous
            # addon configuration incarnation
            curr_game_binding = game.settings.binding

            timer = Timer()
            timer.tick()
            addons_synthesis = game.synthetize()
            timer.tock()
            logger.debug(msg=f"Addon synthesis lasted {timer.delta()} seconds.")

            if curr_settings_digest != prev_settings_digest:
                print_addon_tableau(addons_synthesis, lambda x: logger.info(msg=x))

            if not is_run_only:
                disable_dll_addons(addons_synthesis)
                restore_dll_addons(addons_synthesis)

                updater = AddonUpdater(app_context.config)
                updater.update_addons(addons_synthesis)

            if not is_addon_update_only:
                args = []
                for _ in game.settings.arguments:
                    if not _.meta.is_deprecated and _.enabled:
                        args.append(str(_.synthetize()))

                process.arun(
                    game.config.game_path,
                    game.config.game_root,
                    args
                )

                for addon in addons_synthesis:
                    if addon.binding.is_enabled and addon.binding.is_exe():
                        process.arun(addon.binding.path, addon.binding.path.parent)

            logger.info(msg="Stack complete. Closing...")

    return game is not None

if __name__ == "__main__":

    app = AppContext()

    app.create_app_environment()

    execution_result = run_main(app)

    sys.exit(execution_result)
