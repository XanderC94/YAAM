'''
Application configuration module
'''
from copy import deepcopy
from typing import Any, Dict, Sequence
from pathlib import Path
from configparser import ConfigParser
from yaam.model.options import Option
from yaam.utils.argparse import Parser
from yaam.utils.logger import static_logger as logger

class AppProperty(object):
    '''
    Application configuration property
    '''
    def __init__(self, option: Option, value: Any, volatile: bool = False) -> None:
        super().__init__()
        self.option = option
        self.value = value
        self.volatile = volatile

    def __repr__(self) -> str:
        return super().__str__()

    def __str__(self) -> str:
        return str(self.__dict__)

class AppConfig(object):
    '''
    Application configuration class
    '''

    def __init__(self) -> None:
        super().__init__()
        self.__property_map: Dict[Option, AppProperty] = dict()
        self.__overridden: Dict[Option, AppProperty] = dict()

    def set_property(self, option: Option, value: Any, volatile: bool = False):
        '''
        Set a new value for the specified property
        '''
        if option in self.__property_map:
            obj = self.__property_map[option]
            if volatile and not obj.volatile:
                self.__overridden[option] = deepcopy(obj)
            obj.value = value
            obj.volatile = volatile
        else:
            self.__property_map[option] = AppProperty(option, value, volatile)

    def get_property(self, option: Option) -> Any:
        '''
        Return the specified property value, if exists, otherwise default
        '''
        prop = self.__property_map.get(option)
        return prop.value if prop is not None else option.default

    def load(self, path: Path, args: Sequence[str]):
        '''
        Load application configuration from file
        '''
        self.__load_configuration(path)
        self.__parse_commandline(args)


    def __load_configuration(self, path: Path):

        if path.exists():
            with open(path, encoding='utf-8', mode='r') as _:
                parser = ConfigParser()
                parser.read_file(_)
                if parser.has_section('yaam'):
                    for (key, value) in parser.items('yaam'):
                        opt = Option.from_string(key)
                        if opt is not None:
                            self.set_property(opt, value)

    def __parse_commandline(self, args: Sequence[str]):
        '''
        Load command line arguments
        '''
        parser = Parser()
        namespace = parser.parse(args)
        logger().debug(msg=namespace)

        loaded_options = set([
            Option.from_string(
                _.removeprefix('-').removeprefix('-')
            ) for _ in args
        ])

        for var in vars(namespace):
            option = Option.from_string(var)
            if option is not None and option in loaded_options:
                self.set_property(option, getattr(namespace, var), volatile=True)

    def save(self, path: Path):
        '''
        Save application configuration
        '''
        # to do...
