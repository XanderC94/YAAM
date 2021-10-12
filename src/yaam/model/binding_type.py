'''
'''
from enum import Enum
from typing import Set

class BindingType(Enum):
    '''
    Addon binary binding type
    '''
    AGNOSTIC = (-1, set())
    EXE = (0, set(["exe"]))
    DXGI_9 = (1, set(["dx9", "d3d9"]))
    DXGI_11 = (2, set(["dx11", "d3d11"]))
    DXGI_12 = (3, set(["dx12", "dxgi", "d3d12"]))
    SHADER = (4, set(["shader", "shaders", "reshade"]))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, BindingType):
            return self.index == o.index
        else:
            return False

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return hash(self.index)

    @property
    def aliases(self) -> Set[str]:
        '''
        Return the possible aliases for the binding
        '''
        return self.value[1]

    @property
    def index(self) -> int:
        '''
        Return the integer value of the enumeration
        '''
        return super().value[0]

    @staticmethod
    def from_string(str_repr: str):
        '''
        Return the enum representation of the string
        '''
        render = BindingType.AGNOSTIC

        for bind_type in BindingType:
            if str_repr == bind_type.name or str_repr in bind_type.aliases:
                render = bind_type
                break
        
        return render