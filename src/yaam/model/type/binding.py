'''
Binding types module
'''

from dataclasses import dataclass, field
from enum import Enum
from types import DynamicClassAttribute
from typing import Set
from yaam.utils.counter import ForwardCounter

@dataclass(frozen=True)
class BindingTypeObj(object):
    '''
    BindingType enum object
    '''
    __counter = ForwardCounter()

    index: int = field(init=False, default_factory=__counter.count)
    signature: str = field(default_factory=str)
    aliases: set = field(default_factory=set)
    is_library: bool = field(default=False)
    can_shader: bool = field(default=False)
    shader: str = field(default_factory=str)
    suffix: str = field(default_factory=str)

class BindingType(Enum):
    '''
    Addon binary binding type
    '''

    NONE = BindingTypeObj()
    FILE = BindingTypeObj("file", set())
    EXE = BindingTypeObj("exe", set(), suffix='.exe')
    AGNOSTIC = BindingTypeObj("any", set(["agnostic"]), True, True, "dxgi", '.dll')
    D3D9 = BindingTypeObj("d3d9", set(["dx9"]), True, True, "dxgi", '.dll')
    D3D10 = BindingTypeObj("d3d10", set(["dx10"]), True, True, "dxgi", '.dll')
    D3D11 = BindingTypeObj("d3d11", set(["dx11"]), True, True, "dxgi", '.dll')
    D3D12 = BindingTypeObj("d3d12", set(["dx12"]), True, True, "dxgi", '.dll')
    VULKAN = BindingTypeObj("vulkan", set(["vk"]), True, True, "vk", '.dll')

    def __eq__(self, o: object) -> bool:
        if isinstance(o, BindingType):
            return self.index == o.index
        else:
            return False

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return hash(self.index)

    @DynamicClassAttribute
    def value(self) -> BindingTypeObj:
        '''
        The value of the Enum member.
        '''
        return super().value

    @property
    def index(self) -> int:
        '''
        Return the integer value of the enumeration
        '''
        return self.value.index

    @property
    def signature(self) -> str:
        '''
        Return the preferred alias for the binding
        '''
        return self.value.signature

    @property
    def aliases(self) -> Set[str]:
        '''
        Return the possible aliases for the binding
        '''
        return self.value.aliases

    def is_library(self) -> bool:
        '''
        Return whether this kind of binding is a library (.dll or .lib)
        '''
        return self.value.is_library

    def can_shader(self) -> bool:
        '''
        Return whether this kind of binding can shader
        '''
        return self.value.can_shader

    @property
    def suffix(self) -> str:
        '''
        Return the file suffix for this binding type
        '''
        return self.value.suffix

    @property
    def shader(self) -> str:
        '''
        Return the preferred shader signature for this binding
        '''
        return self.value.shader

    @staticmethod
    def from_string(str_repr: str):
        '''
        Return the enum representation of the string
        '''
        binding = BindingType.NONE

        for _ in BindingType:
            if str_repr == _.name or str_repr == _.signature or str_repr in _.aliases:
                binding = _
                break

        return binding
