'''
Contexts module
'''
import os
from pathlib import Path
from typing import Dict
from dataclasses import dataclass
import shutil
import json

@dataclass(frozen=True)
class GameContext(object):
    '''
    Game context module
    '''
    def __init__(self,
        game_root: Path,
        yaam_game_dir : Path,
        args_path: Path,
        addons_path: Path,
        bindings_path: Path,
        chains_path: Path):

        self.game_root = game_root
        self.yaam_game_dir = yaam_game_dir
        self.args_path = args_path
        self.addons_path = addons_path
        self.bindings_path = bindings_path
        self.chains_path = chains_path

class ApplicationContext(object):
    '''
    Application context class
    '''

    def __init__(self):
        
        self._appdata_dir = Path(os.getenv("APPDATA"))
        self._temp_dir = Path(os.getenv("TEMP"))
        self._yaam_dir = self._appdata_dir / "yaam"
        self._res_dir = self._yaam_dir / "res"
        self._version = str()
        self._yaam_temp_dir = self._temp_dir / "yaam-release"

        self.__game_contexts: Dict[str, GameContext] = dict()

    def create_app_environment(self):
        '''
        Deploy application environment if it doesn't exist
        '''
        os.makedirs(self._yaam_dir, exist_ok=True)
        os.makedirs(self._res_dir, exist_ok=True)

        with open(self._yaam_temp_dir / "MANIFEST", encoding="urf-8", mode="r") as _:
            manifest = json.load(_)
            self._version = manifest['version']

    def create_game_environment(self, game_name: str, game_root: Path) -> GameContext:
        '''
        Create game environment
        '''
        if game_name not in self.__game_contexts:
            
            yaam_game_dir = self._res_dir / game_name
            yaam_game_dir.mkdir(exist_ok=True)

            arguments_path = yaam_game_dir / "arguments.json"
            addons_path = yaam_game_dir / "addons.json"
            bindings_path = yaam_game_dir / "bindings.json"
            chains_path = yaam_game_dir / "chains.json"

            if not arguments_path.exists():
                shutil.copyfile(self._yaam_temp_dir / "res/default" / game_name / "arguments.json", arguments_path)

            if not addons_path.exists():
                shutil.copyfile(self._yaam_temp_dir / "res/default" / game_name / "addons.json", addons_path)

            if not bindings_path.exists():
                shutil.copyfile(self._yaam_temp_dir / "res/default" / game_name / "bindings.json", bindings_path)

            if not chains_path.exists():
                shutil.copyfile(self._yaam_temp_dir / "res/default" / game_name / "chains.json", chains_path)

            self.__game_contexts[game_name] = GameContext(
                game_root,
                yaam_game_dir,
                arguments_path,
                addons_path,
                bindings_path,
                chains_path
            )

        return self.__game_contexts[game_name]

    def game_context(self, game_name: str) -> GameContext:
        '''
        Return the specified game context if exists
        '''
        if game_name in self.__game_contexts:
            return self.__game_contexts[game_name]
        else:
            return None
