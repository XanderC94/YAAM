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
from yaam.model.game.factory import GameFactory, IGame
from yaam.model.mutable.addon_base import AddonBase
from yaam.model.mutable.binding import Binding
from yaam.model.type.binding import BindingType
from yaam.utils import process
from yaam.model.options import Option
from yaam.utils.counter import ForwardCounter
from yaam.utils.logger import init_static_logger, logging
from yaam.utils.print import print_addon_tableau
from yaam.utils.exceptions import ConfigLoadException
from yaam.model.appcontext import AppContext
from yaam.utils.timer import Timer
from yaam.utils.exceptions import exception_handler

#####################################################################


def select_game(app_context: AppContext, logger: logging.Logger) -> str:
    '''
    request or resolve the name of the game to be loaded
    '''
    game_name = app_context.config.get_property(Option.GAME)

    if game_name is None:
        game_list = app_context.game_list()

        i = ForwardCounter()
        for _ in game_list:
            print(f"{i.next()} - {_}")

        if len(game_list) > 0:
            choice = input("Choose the game to load: ")
            if choice.isnumeric() and int(choice) > 0 and int(choice) < i + 1:
                game_name = game_list[int(choice) - 1]
        else:
            logger.error(msg="Game directory is empty...")

    return game_name


def run_yaam(app_context: AppContext, logger: logging.Logger):
    '''
    Main thread
    '''

    game: IGame[AddonBase, Binding] = None
    game_stasis: IGame[AddonBase, Binding] = None
    try:
        game_name = select_game(app_context, logger)
        if game_name is not None:
            game = GameFactory.incarnate(game_name, app_context)
            game_stasis = deepcopy(game)

    except ConfigLoadException as ex:
        logger.info(ex)
    finally:
        if game is not None:
            # is_edit_mode = app_context.config.get_property(Option.EDIT)
            is_addon_update_only = app_context.config.get_property(Option.UPDATE_ADDONS)
            is_run_only = app_context.config.get_property(Option.RUN_STACK)
            # is_export_only = app_context.config.get_property(Option.EXPORT)
            prefetch_updates: bool = not is_run_only
            # ignore_disabled: bool = False
            force_updates: bool = (
                app_context.config.get_property(Option.UPDATE_ADDONS)
                and app_context.config.get_property(Option.FORCE_ACTION)
            )

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
            curr_game_binding: BindingType = game.settings.binding_type

            timer = Timer()
            timer.tick()
            addons_synthesis = game.synthetize()
            timer.tock()
            logger.debug(msg=f"Addon synthesis lasted {timer.delta()} seconds.")

            if curr_settings_digest != prev_settings_digest:
                print_addon_tableau(addons_synthesis, lambda x: logger.info(msg=x))

            with HttpRequestManager(app_context.config) as http:

                addon_updater = AddonUpdater(http)
                meta_collector = MetadataCollector(http, game.context)

                manager = AddonManager(meta_collector, addon_updater, curr_game_binding)
                manager.initialize_metadata(addons_synthesis, prefetch_updates, force_updates)
                manager.resolve_renames(addons_synthesis, prev_addons_synthesis)
                manager.disable_addons(addons_synthesis, prev_addons_synthesis)
                manager.restore_addons(addons_synthesis, prev_addons_synthesis)

                if not is_run_only:
                    manager.update_addons(addons_synthesis, force_updates)

            if not is_addon_update_only:
                # for some reasons compiling this 4 line of code as
                # args = [
                #     str(_.synthetize())
                #     for _ in game.settings.arguments
                #     if not _.meta.is_deprecated and _.enabled
                # ]
                # will make Nuitka go completely bonkers
                # therefore, future me, don't change it again.
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
    _app_context.create_app_environment(sys.argv[0], sys.argv[1:])
    _app_context.deploy_default_init_resources()

    _logger = init_static_logger(
        # logger_name='YAAM',
        log_level=logging.DEBUG if _app_context.is_debug else logging.INFO,
        log_file=_app_context.temp_dir/"yaam.log"
    )

    _logger.debug(msg=_app_context.working_dir)
    _logger.debug(msg=str(_app_context.config))

    execution_result = run_yaam(_app_context, _logger)

    # 0 == success, 1 == failure
    sys.exit(0 if execution_result else 1)
