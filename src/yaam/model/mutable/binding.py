'''
Binding model module
'''
from pathlib import Path
from typing import List
from yaam.model.type.binding import BindingType
from yaam.utils.json.jsonkin import Jsonkin

class Binding(Jsonkin):
    '''
    Mutable Addon binding model
    '''

    def __init__(self,
        name: str = str(),
        path: Path = Path(),
        args: List[str] = None,
        enabled: bool = False,
        updateable: bool = False,
        binding_type: BindingType = BindingType.AGNOSTIC):

        self._name = name
        self._path = path
        self._args = args if args is not None else list()
        self._enabled = enabled
        self._updateable = updateable
        self._binding_type = binding_type

    def __hash__(self) -> int:
        return hash((self.name, self.typing))

    @property
    def name(self) -> str:
        '''
        Returns the Addon name
        '''
        return self._name

    @property
    def path(self) -> Path:
        '''
        Returns the addon path
        '''
        return self._path

    @property
    def is_headless(self) -> bool:
        '''
        Return if its a headless addon (path is a folder)
        '''
        return len(self.path.suffix) == 0

    @property
    def workspace(self) -> Path:
        '''
        Return the addon workspace / parent folder
        '''
        if self.is_headless:
            return self.path
        else:
            return self.path.parent

    @property
    def default_naming(self) -> str:
        '''
        Return the default naming (stem + suffix) of the binding.

        NOTE: this is not the download name.
        '''
        if self.is_headless:
            return ''
        else:
            return self.path.name

    @property
    def default_stem(self) -> str:
        '''
        Return the default naming stem of the binding.

        NOTE: this is not the download name.
        '''
        if self.is_headless:
            return ''
        else:
            return self.path.stem

    @property
    def args(self) -> List[str]:
        '''
        Returns the addon args
        '''
        return self._args

    @property
    def is_updateable(self) -> bool:
        '''
        Returns whether or not this addon should be updated
        '''
        return self._updateable

    @property
    def is_enabled(self) -> bool:
        '''
        Returns whether or not this addon is enabled
        '''
        return self._enabled

    @property
    def typing(self) -> BindingType:
        '''
        Returns the addon binding type
        '''
        return self._binding_type

    def is_dll(self) -> bool:
        '''
        Returns whether this addon is a .dll or not
        '''
        return self._binding_type.is_library()

    def is_file(self) -> bool:
        '''
        Returns whether this addon is a generic file or not
        '''
        return self._binding_type is BindingType.FILE

    def is_exe(self) -> bool:
        '''
        Return whether this addon is an .exe or not
        '''
        return self._binding_type is BindingType.EXE

    @name.setter
    def name(self, new_name : str):
        '''
        Set the Addon name
        '''
        self._name = new_name

    @path.setter
    def path(self, new_path : Path):
        '''
        Set the Addon path
        '''
        self._path = new_path

    @args.setter
    def args(self, new_args : List[str]):
        '''
        Set the Addon path
        '''
        self._args = new_args

    @is_updateable.setter
    def updateable(self, updateable : bool):
        '''
        Set whether or not this addon should be updated
        '''
        self._updateable = updateable

    @is_enabled.setter
    def is_enabled(self, enabled : bool) -> str:
        '''
        Set whether or not this addon is enabled
        '''
        self._enabled = enabled

    @typing.setter
    def typing(self, new_binding : BindingType):
        '''
        Set the addon binding type
        '''
        self._binding_type = new_binding

    @staticmethod
    def from_json(json_obj: dict):
        '''
        Create object representation of this class from dict representation
        '''
        return Binding(
            name=json_obj.get("name", ""),
            path=Path(json_obj.get("path", "")),
            args=json_obj.get("args", []),
            enabled=json_obj.get("enabled", False),
            updateable=json_obj.get("update", False)
        )

    def to_json(self):
        '''
        Map the json rapresentation into an object of this class
        '''
        return {
            'name': self.name,
            'path': str(self.path),
            'args': self.args,
            'enabled': self.is_enabled,
            'update': self.is_updateable
        }
