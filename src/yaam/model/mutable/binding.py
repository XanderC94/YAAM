'''
Binding model module
'''
from pathlib import Path
from yaam.model.type.binding import BindingType
from yaam.utils.json.jsonkin import Jsonkin

class Binding(Jsonkin):
    '''
    Mutable Addon binding model
    '''

    def __init__(self,
        name: str, path: Path = Path(),
        enabled: bool = False, updateable: bool = False,
        binding_type: BindingType = BindingType.AGNOSTIC):

        self._name = name
        self._path = path
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
    def updateable(self) -> bool:
        '''
        Returns whether or not this addon should be updated
        '''
        return self._updateable

    @property
    def enabled(self) -> bool:
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
        return self._binding_type.suffix == ".dll" or (
            self._binding_type == BindingType.AGNOSTIC and
            ".dll" in self._path.name
        )

    def is_exe(self) -> bool:
        '''
        Return whether this addon is an .exe or not
        '''
        return self._binding_type.suffix == ".exe" or self._path.suffix == ".exe"

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

    @updateable.setter
    def updateable(self, updateable : bool):
        '''
        Set whether or not this addon should be updated
        '''
        self._updateable = updateable

    @enabled.setter
    def enabled(self, enabled : bool) -> str:
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
            json_obj["name"],
            Path(json_obj.get("path", "")),
            json_obj.get("enabled", False),
            json_obj.get("update", False)
        )

    def to_json(self):
        '''
        Map the json rapresentation into an object of this class
        '''
        return {
            'name': self.name,
            'path': str(self.path),
            'enabled': self.enabled,
            'update': self.updateable
        }
