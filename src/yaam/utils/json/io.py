'''
JSON I/O utilities functions
'''

import json
from typing import Dict
from pathlib import Path
from yaam.utils.functional import identity, Consumer, Mapper, K
from yaam.utils.json.repr import jsonrepr

def read_json(path: Path or str, encoding='utf8', decerealize : Mapper[dict, K]=identity) -> K or dict:
    '''
    Read raw json obj from file
    '''
    _obj = dict()

    if path.exists():
        try:

            with open(path, 'r', encoding=encoding) as _:
                _obj = decerealize(json.load(_))
        except IOError as _:
            _obj = dict()
        except json.decoder.JSONDecodeError as _:
            _obj = dict()

    return _obj

def write_json(obj, path: Path or str, encoding='utf8', indent = 4, cerealize=jsonrepr):
    '''
    Write json obj to file
    '''
    try:
        with open(path, 'w', encoding=encoding) as _:
            json.dump(obj, _, indent=indent, default=cerealize)
    except IOError as _:
        pass
    except json.decoder.JSONDecodeError as _:
        pass

def consume_json_entries(json_obj: dict, consumers: Dict[str, Consumer]):
    '''
    Read json and map-consume by entries
    '''
    for (key, consumer) in consumers.items():
        if key in json_obj:
            consumer(json_obj[key])
