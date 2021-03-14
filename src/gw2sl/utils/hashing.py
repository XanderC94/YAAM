'''
Hashing utility functions
'''
import hashlib

from enum import Enum
from pathlib import Path

import requests

class HashType(Enum):
    '''
    Available hashing algorithms
    '''
    NONE = (-1, set()),
    MD5 = (0, set(['MD5', 'MD5SUM'])),
    SHA1 = (1, set(['SHA1'])),
    SHA256 = (2, set(['SHA256', 'SHA'])),
    SHA384 = (3, set(['SHA384'])),
    SHA512 = (4, set(['SHA512']))

    @staticmethod
    def from_string(str_repr: str):
        '''
        Get enum type from strin repr.
        If none match return NONE
        '''
        result = HashType.NONE

        for hash_type in HashType:
            if str_repr.upper() in hash_type.value[0][1]:
                result = hash_type
                break

        return result


def make_hash(fname, fshan=hashlib.md5()):
    '''
    Return hashcode for the specified fiel with the specified algoritm
    '''
    with open(fname, "rb") as file_to_hash:
        for chunk in iter(lambda: file_to_hash.read(4096), b""):
            fshan.update(chunk)
    return fshan.hexdigest()

def get_remote_hash(url: str):
    '''
    Retreive a remote hash from the provided url

    @url: str -- address of the hash
    '''
    hash_code = str()
    hash_type = HashType.NONE

    tokens = url.split('.')

    if tokens:
        hash_type = HashType.from_string(tokens[-1])

    res = requests.get(url)
    hash_code = res.content.decode(encoding='utf-8', errors='ignore')

    split = ['\n', '\r', ' ']

    for element in split:
        tokens = hash_code.split(sep=element)
        for token in tokens:
            if token:
                hash_code = token
                break

    purge = ["\x00"]

    for element in purge:
        hash_code = hash_code.replace(element, "")

    return (hash_code.upper(), hash_type)

def get_local_hash(path: Path, hash_type: HashType):
    '''
    Retreive a remote hash from the provided url

    @path: Path -- path to the file for which computing the hash
    '''
    hash_code = str()

    if hash_type == HashType.MD5:
        hash_code = make_hash(path)
    elif hash_type == HashType.SHA1:
        hash_code = make_hash(path, hashlib.sha1())
    elif hash_type == HashType.SHA256:
        hash_code = make_hash(path, hashlib.sha256())
    elif hash_type == HashType.SHA384:
        hash_code = make_hash(path, hashlib.sha384())
    elif hash_type == HashType.SHA512:
        hash_code = make_hash(path, hashlib.sha512())

    return hash_code.upper()

