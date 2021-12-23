'''
REPL state module
'''

from enum import Enum
from distutils.util import strtobool
from pathlib import Path
from typing import Any, Callable, Dict
from yaam.model.game.base import Game, AddonBase, Binding
from yaam.controller.cmd.state.base import AREPLState
from yaam.controller.cmd.state.validators import YesValidator
from yaam.controller.cmd.state.validators import AddonNameValidator, AddonURIValidator
from yaam.controller.cmd.state.validators import BindingNameValidator, BindingPathValidator, BindingTypeValidator
from yaam.model.type.binding import BindingType

class LUTEntry:
    '''
    Game entity properties look-up table
    '''
    def __init__(self, 
            attribute : str = "", 
            typing : object = None, 
            optional : bool = False, 
            validator : Callable = YesValidator(), 
            handle : Callable = lambda x, y: None, 
            description : str = ""):

        self.attribute = attribute
        self.typing = typing
        self.optional = optional
        self.validator = validator
        self.handle = handle
        self.description = description

class CreateMode(object):
    '''
    Enum class object type
    '''
    __counter : int = -1

    def __init__(self, entity : Callable = lambda x : None, lut : dict = None):
        self.__index : int = CreateMode.__increment()
        self.__entity = entity
        self.__lut = lut

    @staticmethod
    def __increment() -> int:
        CreateMode.__counter += 1
        return CreateMode.__counter

    @property
    def index(self) -> int:
        '''
        Return object auto index
        '''
        return self.__index

    @property
    def entity(self) -> Callable:
        '''
        Return associated entity constructor
        '''
        return self.__entity

    @property
    def lut(self) -> dict:
        '''
        Return associated entity properties' look-up table
        '''
        return self.__lut

class REPLCreateMode(Enum):
    '''
    REPL creation state mode
    '''

    NONE = CreateMode(None, dict())

    ADDON = CreateMode(AddonBase, dict({
        'name': LUTEntry(
            attribute="name",
            typing=str, optional=False,
            validator=AddonNameValidator(),
            handle=AddonBase.name.__set__,
            description="""
            Name of the addon
            """
        ),
        'uri': LUTEntry(
            attribute="uri",
            typing=str, optional=False,
            validator=AddonURIValidator(),
            handle=AddonBase.uri.__set__,
            description="""
            Addon download URI
            """
        ),
        'is_shader': LUTEntry(
            attribute="is_shader",
            typing=bool, optional=True,
            validator=YesValidator(),
            handle=lambda obj, val: AddonBase.is_shader.__set__(obj, bool(strtobool(val))),
            description="""
            Specify whether or not this addon is a shader dll or not
            """
        ),
        'descr': LUTEntry(
            attribute="description",
            typing=str, optional=True,
            validator=YesValidator(),
            handle=AddonBase.description.__set__,
            description="""
            A short descrition about this addon
            """
        ),
        'dependecies': LUTEntry(
            attribute="dependencies",
            typing=list, optional=True,
            validator=YesValidator(),
            handle=lambda obj, val: AddonBase.dependencies.__set__(obj, val.split(',')),
            description="""
            A comma separated list of this addon dependencies 
            (other addons on which this addon depends on to work correctly)
            """
        ),
        'contribs': LUTEntry(
            attribute="contributors",
            typing=list, optional=True,
            validator=YesValidator(),
            handle=lambda obj, val: AddonBase.contributors.__set__(obj, val.split(',')),
            description="""
            A comma separated list of this addon developement contributors 
            """
        ),
        'chainloads': LUTEntry(
            attribute="chainloads",
            typing=list, optional=True,
            validator=YesValidator(),
            handle=lambda obj, val: AddonBase.chainloads.__set__(obj, val.split(',')),
            description="""
            A comma separated list of this addon chainload names in order of preference 
            """
        )
    }))

    BINDING = CreateMode(Binding, dict({
        'name': LUTEntry(
            attribute="name",
            typing=str, optional=False,
            validator=BindingNameValidator(),
            handle=Binding.name.__set__,
            description="""
            Name of the addon to which associate this binding
            """
        ),
        'path': LUTEntry(
            attribute="path",
            typing=Path, optional=False,
            validator=BindingPathValidator(),
            handle=lambda obj, val: Binding.path.__set__(obj, Path(val)),
            description="""
            Path to which the associated addon should be deployed
            """
        ),
        'type': LUTEntry(
            attribute="typing",
            typing=BindingType, optional=False,
            validator=BindingTypeValidator(),
            handle=lambda obj, val: Binding.typing.__set__(obj, BindingType.from_string(val)),
            description=f"""
            Type of the binding to associate to the addon.
            Accepted values:
            \t{', '.join([_.name.lower() for _ in BindingType if _ is not BindingType.NONE])}
            """
        ),
        'enabled': LUTEntry(
            attribute="enabled",
            typing=bool, optional=True,
            validator=YesValidator(),
            handle=lambda obj, val: Binding.enabled.__set__(obj, bool(strtobool(val))),
            description="""
            Specify whether this addon binding is enabled or not
            """
        ),
        'update': LUTEntry(
            attribute="updateable",
            typing=bool, optional=True,
            validator=YesValidator(),
            handle=lambda obj, val: Binding.updateable.__set__(obj, bool(strtobool(val))),
            description="""
            Specify whether this addon binding should be updated or not
            """
        )
    }))

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, REPLCreateMode):
            return hash(self) == hash(obj)
        else:
            return super().__eq__(obj)

    def __hash__(self) -> int:
        return hash(tuple([self.index, self.signature]))

    @property
    def index(self) -> int:
        '''
        Mode index
        '''
        return self.value.index

    @property
    def signature(self) -> str:
        '''
        Mode signature
        '''
        return self.name.lower()

    def new_entity(self) -> Any:
        '''
        Entity builder
        '''
        return self.value.entity()

    @property
    def lut(self) -> Dict[str, LUTEntry]:
        '''
        Entity properties lut
        '''
        return self.value.lut

    def parse(self, command: str) -> tuple:
        '''
        Parse REPL command
        '''
        return tuple(command.split('=', 1))

    @staticmethod
    def from_string(str_repr:str):
        '''
        Return this enum obj from string repr
        '''
        mode = REPLCreateMode.NONE

        for enum in REPLCreateMode:
            if enum.name == str_repr or enum.signature == str_repr:
                mode = enum
                break

        return mode

#######################################################################################

class REPLCreateState(AREPLState):
    '''
    REPL entity creation state
    '''

    def __init__(self,
        name: str, mode: REPLCreateMode, game: Game,
        completekey: str = 'tab', stdin=None, stdout=None) -> None:

        super().__init__(f"{name}-{mode.signature}", game, completekey=completekey, stdin=stdin, stdout=stdout)
        self.__mode = mode
        self.__entity = mode.new_entity()
        self._set_properties = set()
        self._completed = False

    @property
    def mode(self) -> REPLCreateMode:
        '''
        Return the state mode
        '''
        return self.__mode

    def help_set(self):
        '''
        set helper method
        '''

        params = ' | '.join([f'{_}' for _ in self.__mode.lut.keys()])

        self.stdout.writelines([
            f'Set entity properties for {self.mode.signature}\n\n',
            f'set <{params}>=[value]\t(Example: set name=bob)\n\n',
            '\n'.join([
                f'\t{key} ({_.typing.__name__}, optional={str(_.optional)}){_.description}'
                for (key, _) in self.__mode.lut.items()
            ]),
            "\n\n"
        ])

    def do_set(self, args: str):
        '''
        Set entity properties
        '''

        (prop, value) = self.__mode.parse(args)

        self.stdout.write(f"{prop} <- {value}\n")

        if prop in self.__mode.lut:
            try:
                if self.mode.lut[prop].validator(self._game, value):
                    self.mode.lut[prop].handle(self.__entity, value)
                    self._set_properties.add(prop)
                else:
                    raise ValueError(self.mode.lut[prop].validator.error_msg)
            except ValueError as _:
                self.stdout.write(str(_))
            else:
                self.stdout.write(f"{prop}: {getattr(self.__entity, self.mode.lut[prop].attribute)}\n")
        else:
            self.stdout.write(f'{self.mode.signature} has no property {prop}\n')

        return False

    def _can_complete(self, _: str) -> bool:
        self._completed = False

        for (key, entry) in self.__mode.lut.items():
            self._completed = entry.optional or key in self._set_properties

        return self._completed

    def postloop(self) -> None:

        if self._completed:
            
            self.stdout.write(f"{str(self.__entity)}\n")

            if self.__mode == REPLCreateMode.ADDON and isinstance(self.__entity, AddonBase):
                self._game.settings.bases[self.__entity.name] = self.__entity
            elif self.__mode == REPLCreateMode.BINDING and isinstance(self.__entity, Binding):
                self._game.settings.bindings[self.__entity.typing][self.__entity.name] = self.__entity
            
        return super().postloop()
