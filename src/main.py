'''
YAAM main module
'''

import sys
from copy import deepcopy
# from yaam.controller.cmd.repl import repl
from yaam.controller.http import HttpRequestManager
from yaam.controller.metadata import MetadataCollector
from yaam.controller.update.updater import AddonUpdater
from yaam.controller.manage import AddonManager
from yaam.model.game.base import Game
from yaam.utils import process
from yaam.model.options import Option
from yaam.utils.logger import init_static_logger, logging
from yaam.utils.print import print_addon_tableau
from yaam.model.game.gw2 import GuildWars2
from yaam.utils.exceptions import ConfigLoadException
from yaam.model.context import AppContext
from yaam.utils.timer import Timer
from yaam.utils.exceptions import exception_handler

#####################################################################

def run_main(app_context : AppContext, logger: logging.Logger):
    '''
    Main thread
    '''

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
            # is_edit_mode = app_context.config.get_property(Option.EDIT)
            is_addon_update_only = app_context.config.get_property(Option.UPDATE_ADDONS)
            is_run_only = app_context.config.get_property(Option.RUN_STACK)
            # is_export_only = app_context.config.get_property(Option.EXPORT)

            # prev_game_binding = game_stasis.settings.binding_type
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
            curr_game_binding = game.settings.binding_type

            timer = Timer()
            timer.tick()
            addons_synthesis = game.synthetize()
            timer.tock()
            logger.debug(msg=f"Addon synthesis lasted {timer.delta()} seconds.")

            if curr_settings_digest != prev_settings_digest:
                print_addon_tableau(addons_synthesis, lambda x: logger.info(msg=x))

            if not is_run_only:
                with HttpRequestManager(app_context.config) as http:
                    meta_collector = MetadataCollector(http)
                    meta_collector.load_local_metadata(addons_synthesis)

                    manager = AddonManager(meta_collector, curr_game_binding)
                    manager.resolve_renames(addons_synthesis, prev_addons_synthesis)
                    manager.disable_addons(addons_synthesis, prev_addons_synthesis)
                    manager.restore_addons(addons_synthesis, prev_addons_synthesis)

                    updater = AddonUpdater(app_context.config, meta_collector, http)
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
                        process.arun(addon.binding.path, addon.binding.path.parent, addon.binding.args)

            logger.info(msg="Stack complete. Closing...")

    return game is not None

if __name__ == "__main__":

    sys.excepthook = exception_handler

    _app_context = AppContext()
    _app_context.create_app_environment()

    _logger = init_static_logger(
        # logger_name='YAAM',
        log_level=logging.DEBUG if _app_context.debug else logging.INFO,
        log_file=_app_context.temp_dir/"yaam.log"
    )

    _logger.debug(msg=_app_context.working_dir)
    _logger.debug(msg=str(_app_context.config))

    execution_result = run_main(_app_context, _logger)

    sys.exit(execution_result)
