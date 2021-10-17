'''
Contexts module
'''
import os
from pathlib import Path
import sys
from typing import Dict, Sequence
from dataclasses import dataclass, field
import shutil
import json

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
    bindings_path  : Path = field(init=True)
    chains_path    : Path = field(init=True)

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
        self._version = str()
        self._yaam_temp_dir = self._temp_dir / "yaam-release" if not debug else self._work_dir
        
        self._execution_path = Path()

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

        if not self._debug:
            with open(self._yaam_temp_dir / "MANIFEST", encoding="urf-8", mode="r") as _:
                manifest = json.load(_)
                self._version = manifest['version']

        vargs = sys.argv
        self._execution_path = vargs[0]
        self._app_config.load(self._yaam_dir / "config.yaml", vargs[1:])

    def create_game_environment(self, game_name: str, game_root: Path) -> GameContext:
        '''
        Create game environment
        '''
        if game_name not in self._game_contexts:

            yaam_game_dir = self._res_dir / game_name
            yaam_game_dir.mkdir(exist_ok=True)

            arguments_path = yaam_game_dir / "arguments.json"
            addons_path = yaam_game_dir / "addons.json"
            bindings_path = yaam_game_dir / "bindings.json"
            chains_path = yaam_game_dir / "chains.json"

            tmp_yaam_game_dir = self._yaam_temp_dir / "res/default" / game_name

            if not arguments_path.exists():
                shutil.copyfile(tmp_yaam_game_dir / "arguments.json", arguments_path)

            if not addons_path.exists():
                shutil.copyfile(tmp_yaam_game_dir / "addons.json", addons_path)

            if not bindings_path.exists():
                shutil.copyfile(tmp_yaam_game_dir / "bindings.json", bindings_path)

            if not chains_path.exists():
                shutil.copyfile(tmp_yaam_game_dir / "chains.json", chains_path)

            self._game_contexts[game_name] = GameContext(
                game_root,
                yaam_game_dir,
                arguments_path,
                addons_path,
                bindings_path,
                chains_path
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
