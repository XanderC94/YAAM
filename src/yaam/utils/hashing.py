'''
Hashing utility functions
'''
import hashlib
from enum import Enum
from pathlib import Path


class Hasher(Enum):
    '''
    Available hashing algorithms
    '''
    NONE = 0,
    MD5 = 1,
    SHA1 = 2,
    SHA256 = 3,
    SHA384 = 4,
    SHA512 = 5

    def create(self):
        '''
        Create strategy for the current enum value
        '''
        strategy = None

        if self == Hasher.MD5:
            strategy = hashlib.md5()
        elif self == Hasher.SHA1:
            strategy = hashlib.sha1()
        elif self == Hasher.SHA256:
            strategy = hashlib.sha256()
        elif self == Hasher.SHA384:
            strategy = hashlib.sha384()
        elif self == Hasher.SHA512:
            strategy = hashlib.sha512()

        return strategy

    def make_hash_from_file(self, fname: Path) -> str:
        '''
        Return hashcode for the specified file with the specified algorithm
        @fname: Path -- path to the file for which computing the hash
        '''
        fshan = self.create()

        if fname.is_file():
            with open(fname, "rb") as file_to_hash:
                for chunk in iter(lambda: file_to_hash.read(4096), b""):
                    fshan.update(chunk)
        else:
            return ''

        return fshan.hexdigest()

    def make_hash_from_bytes(self, data: bytes) -> str:
        '''
        Return hashcode for the specified bytes
        @data: bytes -- data byte to hash
        '''
        fshan = self.create()
        fshan.update(data)
        return fshan.hexdigest()

    def make_hash_from_string(self, data: str, encoding: str = "utf-8", errors: str = "strict") -> str:
        '''
        Return hashcode for the specified string
        @data: str -- data string to hash
        '''
        fshan = self.create()
        fshan.update(data.encode(encoding=encoding, errors=errors))
        return fshan.hexdigest()

    @staticmethod
    def from_string(str_repr: str):
        '''
        Get enum type from string repr.
        If none match return NONE
        '''
        result = Hasher.NONE

        for hasher in Hasher:
            if str_repr.upper() == hasher.name:
                result = hasher
                break

        return result
