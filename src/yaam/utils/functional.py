'''
Lambdas and functional utilities
'''

from typing import Callable, Dict, Tuple, TypeVar

T = TypeVar('T')
K = TypeVar('K')

Mapper = Callable[[T], K]
Consumer = Callable[[T], None]
SwissKnife = Dict[str, Tuple[Mapper, Consumer]]

def identity(_: T) -> T:
    '''
    Identity function
    '''
    return _
