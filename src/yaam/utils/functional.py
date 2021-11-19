'''
Lambdas and functional utilities
'''

from typing import Any, Callable, Dict, Tuple

Mapper = Callable[[Any], Any]
Consumer = Callable[[Any], None]
SwissKnife = Dict[str, Tuple[Mapper, Consumer]]

def identity(_: Any) :
    '''
    Identity function
    '''
    return _
