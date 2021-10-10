'''
Binding model module
'''
from pathlib import Path
from yaam.model.binding_type import BindingType

class Binding(object):
    '''
    Immutable Addon binding model
    '''

    def __init__(self,
        name: str, path: Path = Path(),
        enabled: bool = False, update: bool = False,
        binding_type: BindingType = BindingType.AGNOSTIC):

        self._name = name
        self._path = path
        self._enabled = enabled
        self._update = update
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
    def is_updateable(self) -> bool:
        '''
        Returns whether or not this addon should be updated
        '''
        return self._update

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
        return self._path.suffix == ".dll"

    def is_exe(self) -> bool:
        '''
        Return whether this addon is an .exe or not
        '''
        return self._path.suffix == ".exe"

    @staticmethod
    def from_dict(json:dict, binding_type: BindingType):
        '''
        Create object representation of this class from dict representation
        '''
        return Binding(
            json["name"],
            Path(json["path"]),
            json["enabled"] if "enabled" in json else False,
            json["update"] if "update" in json else False,
            binding_type
        )