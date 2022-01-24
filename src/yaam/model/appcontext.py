'''
Contexts module
'''
import os
import shutil
from typing import Dict, List
from pathlib import Path
from dataclasses import dataclass, field
from yaam.model.options import Option
from yaam.model.appconfig import AppConfig
from yaam.utils.json.io import write_json, read_json


@dataclass(frozen=True)
class GameContext(object):
    '''
    Game context module
    '''
    game_root: Path = field(init=True)
    yaam_game_dir: Path = field(init=True)
    args_path: Path = field(init=True)
    addons_path: Path = field(init=True)
    settings_path: Path = field(init=True)
    naming_map_path: Path = field(init=True)


class AppContext(object):
    '''
    Application context class
    '''

    def __init__(self):
        self._appdata_dir = Path(os.getenv("APPDATA"))
        self._local_appdata_dir = Path(os.getenv("LOCALAPPDATA"))
        self._temp_dir = Path(os.getenv("TEMP"))
        self._work_dir = Path(os.getcwd())
        self._yaam_dir = self._local_appdata_dir / "yaam"
        self._games_dir = self._yaam_dir / "games"
        self._version = ""

        self._execution_path = Path()
        self._deployment_dir = Path()

        self._game_contexts: Dict[str, GameContext] = dict()

        self._app_config = AppConfig()

    @property
    def is_debug(self) -> bool:
        '''
        Return if the application is running in debug mode
        '''
        return self._app_config.get_property(Option.DEBUG)

    @property
    def config(self) -> AppConfig:
        '''
        Return the application configuration
        '''
        return self._app_config

    @property
    def appdata_dir(self) -> Path:
        '''
        Returns the %APPDATA% directory of the current system
        '''
        return self._appdata_dir

    @property
    def local_appdata_dir(self) -> Path:
        '''
        Returns the %LOCALAPPDATA% directory of the current system
        '''
        return self._local_appdata_dir

    @property
    def temp_dir(self) -> Path:
        '''
        Returns the %TEMP% directory of the current system
        '''
        return self._temp_dir

    @property
    def working_dir(self) -> Path:
        '''
        Returns the current working directory
        '''
        return self._work_dir

    @property
    def deployment_dir(self) -> Path:
        '''
        Returns the deployment directory
        '''
        return self._deployment_dir

    @property
    def yaam_dir(self) -> Path:
        '''
        Returns the yaam data directory
        '''
        return self._yaam_dir

    def init_file_path(self, game_name: str) -> Path:
        '''
        Return the path to the requested game init file
        '''
        return self._games_dir / game_name / "init.json"

    def create_app_environment(self, exec_path: Path, vargs: List[str]):
        '''
        Deploy application environment if it doesn't exist
        '''

        os.makedirs(self._yaam_dir, exist_ok=True)
        os.makedirs(self._games_dir, exist_ok=True)

        self._app_config.load(self._yaam_dir / "yaam.ini", vargs)
        self._execution_path = Path(exec_path)
        self._deployment_dir = self._execution_path.parent
        # If calling the python script, navigate 1 level back in the directory tree
        if self._execution_path.suffix == ".py":
            self._deployment_dir = self._deployment_dir.parent

        manifest: dict = read_json(self._deployment_dir / "MANIFEST")
        self._version = manifest.get('version', '0.0.0.0').join('-debug' if self.is_debug else '-release')

    def deploy_default_init_resources(self) -> None:
        '''
        Copy default game init resources to local if they don't exists
        '''

        default_res_path = self._deployment_dir / "res/default"

        for game_path in default_res_path.iterdir():

            if game_path.is_dir():

                yaam_game_dir = self._games_dir / game_path.name
                yaam_game_dir.mkdir(exist_ok=True)

                def_yaam_game_dir = default_res_path / game_path.name

                init_file_path = yaam_game_dir / "init.json"
                def_init_file_path = def_yaam_game_dir / "init.json"

                if def_init_file_path.exists() and not init_file_path.exists():
                    shutil.copyfile(def_init_file_path, init_file_path)

    def create_game_environment(self, game_name: str, game_root: Path) -> GameContext:
        '''
        Create game environment
        '''
        if game_name not in self._game_contexts:

            yaam_game_dir = self._games_dir / game_name
            yaam_game_dir.mkdir(exist_ok=True)

            arguments_path = yaam_game_dir / "arguments.json"
            addons_path = yaam_game_dir / "addons.json"
            settings_path = yaam_game_dir / "settings.json"
            naming_map_path = yaam_game_dir / "namings.json"

            tmp_yaam_game_dir = self._deployment_dir / "res/default" / game_name

            if tmp_yaam_game_dir.exists():
                if not arguments_path.exists() and (tmp_yaam_game_dir / "arguments.json").exists():
                    shutil.copyfile(tmp_yaam_game_dir / "arguments.json", arguments_path)

                if not addons_path.exists() and (tmp_yaam_game_dir / "addons.json").exists():
                    shutil.copyfile(tmp_yaam_game_dir / "addons.json", addons_path)

                if not settings_path.exists() and (tmp_yaam_game_dir / "settings.json").exists():
                    shutil.copyfile(tmp_yaam_game_dir / "settings.json", settings_path)

                if not naming_map_path.exists() and (tmp_yaam_game_dir / "namings.json").exists():
                    shutil.copyfile(tmp_yaam_game_dir / "namings.json", naming_map_path)
            else:

                if not arguments_path.exists():
                    write_json(dict({'arguments': []}), arguments_path)

                if not addons_path.exists():
                    write_json(dict({'addons': []}), addons_path)

                if not settings_path.exists():
                    write_json(dict({'arguments': [], 'bindings': []}), settings_path)

                if not naming_map_path.exists():
                    write_json(dict({'namings': {}}), naming_map_path)

            self._game_contexts[game_name] = GameContext(
                game_root,
                yaam_game_dir,
                arguments_path,
                addons_path,
                settings_path,
                naming_map_path
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

    def game_list(self) -> List[str]:
        '''
        Return the available games
        '''
        return [_.name for _ in self._games_dir.iterdir() if _.is_dir()]
