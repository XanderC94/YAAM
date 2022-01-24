'''
JSON utilities module
'''

import importlib
from typing import Callable
from types import FunctionType


class Jsonkin(object):
    """
    A mixin class that enable json serialization and deserialization
    for the objects of the inheriting classes
    """
    def to_json(self) -> dict:
        """
        Return a (valid) json representation of the object as a dictionary
        """
        return vars(self)

    @staticmethod
    def from_json(json_obj: dict):
        """
        Map the json rapresentation into an object of this class
        """
        return Jsonkin(**json_obj)

    def __str__(self):
        return str(self.to_json())

    def __repr__(self):
        return str(self.to_json())


###############################################################


def tuple_to_json(tobj: tuple) -> dict:
    '''
    Convert tuple object to json obj
    '''
    return dict((str(k), tobj[k]) for k in range(len(tobj)))


def tuple_from_json(json_obj: dict) -> tuple:
    '''
    Convert json obj to tuple
    '''
    return tuple(json_obj[k] for k in json_obj)


################################################################


class FunctionWrapper(Jsonkin, Callable[[object], object]):
    '''
    Json serializer / deserializer for strings reprensenting a function module path
    '''
    def __init__(self, definition: str or FunctionType):

        if callable(definition):
            self.__fnpointer = definition
            self.__def = f'{definition.__module__}::{definition.__name__}'
        elif isinstance(definition, str):
            self.__fnpointer = None
            self.__def = definition
        else:
            raise TypeError('Function definition is neither a name.space::func_name string or a function object!')

    def __call__(self, *args, **kwargs):
        # Lazy
        if self.__fnpointer is None:
            modulestr, methodstr = self.__def.split('::', 1)
            module = importlib.import_module(modulestr)
            self.__fnpointer = getattr(module, methodstr)

        return self.__fnpointer(*args, **kwargs)

    def to_json(self):
        '''
        Return a (valid) json representation of the object as a dictionary
        '''
        return self.__def

    @staticmethod
    def from_json(json_obj):
        '''
        Map the json rapresentation into an object of this class
        '''
        return FunctionWrapper(json_obj)
