'''
Contexts module
'''
import os
from pathlib import Path
import sys
from typing import Dict
from dataclasses import dataclass, field
from yaam.utils.json.io import write_json, read_json
import shutil

from yaam.model.config import AppConfig

@dataclass(frozen=True)
class GameContext(object):
    '''
    Game context module
    '''
    game_root      : Path = field(init=True)
    yaam_game_dir  : Path = field(init=True)
    args_path      : Path = field(init=True)
    addons_path    : Path = field(init=True)
    settings_path  : Path = field(init=True)

class AppContext(object):
    '''
    Application context class
    '''

    def __init__(self, debug = False):
        self._debug = debug
        self._appdata_dir = Path(os.getenv("APPDATA"))
        self._temp_dir = Path(os.getenv("TEMP"))
        self._work_dir = Path(os.getcwd())
        self._yaam_dir = self._appdata_dir / "yaam"
        self._res_dir = self._yaam_dir / "res"
        self._version = ""

        self._execution_path = Path()
        self._deployment_dir = Path()

        self._game_contexts: Dict[str, GameContext] = dict()
        self._app_config = AppConfig()

    @property
    def debug(self):
        '''
        Return if the application is running in debug mode
        '''
        return self._debug

    @property
    def config(self):
        '''
        Return the application configuration
        '''
        return self._app_config

    @property
    def appdata_dir(self) -> Path:
        '''
        Returns the APPDATA directory of the current system
        '''
        return self._appdata_dir

    def create_app_environment(self):
        '''
        Deploy application environment if it doesn't exist
        '''
        os.makedirs(self._yaam_dir, exist_ok=True)
        os.makedirs(self._res_dir, exist_ok=True)

        vargs = sys.argv

        self._execution_path = Path(vargs[0])
        self._deployment_dir = self._work_dir if self.debug else self._execution_path.parent

        manifest : dict = read_json(self._deployment_dir / "MANIFEST")
        self._version = manifest.get('version', '0.0.0.0').join('d' if self._debug else '')

        self._app_config.load(self._yaam_dir / "yaam.ini", vargs[1:])

    def create_game_environment(self, game_name: str, game_root: Path) -> GameContext:
        '''
        Create game environment
        '''
        if game_name not in self._game_contexts:

            yaam_game_dir = self._res_dir / game_name
            yaam_game_dir.mkdir(exist_ok=True)

            arguments_path = yaam_game_dir / "arguments.json"
            addons_path = yaam_game_dir / "addons.json"
            settings_path = yaam_game_dir / "settings.json"

            tmp_yaam_game_dir = self._deployment_dir / "res/default" / game_name

            if tmp_yaam_game_dir.exists():
                if not arguments_path.exists():
                    shutil.copyfile(tmp_yaam_game_dir / "arguments.json", arguments_path)

                if not addons_path.exists():
                    shutil.copyfile(tmp_yaam_game_dir / "addons.json", addons_path)

                if not settings_path.exists():
                    shutil.copyfile(tmp_yaam_game_dir / "settings.json", settings_path)
            else:
                if not arguments_path.exists():
                    write_json(dict({'arguments':[] }), arguments_path)

                if not addons_path.exists():
                    write_json(dict({'addons':[] }), addons_path)

                if not settings_path.exists():
                    write_json(dict({'arguments': [], 'bindings': []}), settings_path)

            self._game_contexts[game_name] = GameContext(
                game_root,
                yaam_game_dir,
                arguments_path,
                addons_path,
                settings_path
            )

        return self._game_contexts[game_name]

    def game_context(self, game_name: str) -> GameContext:
        '''
        Return the specified game context if exists
        '''
        if game_name in self._game_contexts:
            return self._game_contexts[game_name]
        else:
            return None
