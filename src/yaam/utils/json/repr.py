'''
JSON and objects representation utilities
'''

from typing import Iterable
from pathlib import Path
from yaam.utils.json.jsonkin import Jsonkin

def jsonrepr(obj) -> dict or str or list or float or int:
    '''
    Serializer from object to JSON repr
    '''
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, Jsonkin) or issubclass(type(obj), Jsonkin):
        return obj.to_json()
    elif isinstance(obj, Path):
        return str(obj)
    elif isinstance(obj, float) and obj in (float('inf'), float('+inf'), float('-inf')):
        return str(obj)
    elif isinstance(obj, dict):
        return dict((k, jsonrepr(v)) for k, v in obj.items())
    elif isinstance(obj, Iterable):
        return [ jsonrepr(i) for i in obj ]
    elif hasattr(obj, '__dict__'):
        return vars(obj)
    else:
        return obj

def objrepr(json_repr, obj_type, alt_type=None):
    '''
    Deserializer from JSON repr to defined object type
    '''

    def __go(json_repr, obj_type, alt_type=None):
        '''
        '''
        if isinstance(json_repr, dict) and issubclass(obj_type, Jsonkin):
            return obj_type.from_json(json_repr)
        elif alt_type:

            # if isinstance(alt_type, (tuple, list)):
            #     for t in alt_type:
            #         rep = go(json_repr, obj_type, t)
            #         if rep is not None:
            #             return rep

            if isinstance(json_repr, Iterable) and issubclass(alt_type, Iterable):
                if issubclass(alt_type, dict):
                    if isinstance(json_repr, dict):
                        return alt_type((k, objrepr(v, obj_type, alt_type)) for k, v in json_repr.items())
                else:
                    return alt_type(objrepr(item, obj_type, alt_type) for item in json_repr)

        return obj_type(json_repr)

    if isinstance(json_repr, list):
        return [__go(i, obj_type, alt_type) for i in json_repr]
    else:
        return __go(json_repr, obj_type, alt_type)
