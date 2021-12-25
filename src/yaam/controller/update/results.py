'''
Update results module
'''
from enum import IntEnum, auto

class UpdateResult(IntEnum):
    '''
    Possible results of addon update
    '''
    NONE = 0

    # OK
    TO_CREATE = auto()
    TO_UPDATE = auto()
    UP_TO_DATE = auto()
    UPDATE_METADATA = auto()
    UNPACKING_OK = auto()
    CREATED = auto()
    UPDATED = auto()

    # ERRORS
    INVALID_URL = auto()
    INVALID_ZIP = auto()
    DISABLED = auto()
    NO_UPDATE = auto()
    UNPACKING_FAILED = auto()
    CREATE_FAILED = auto()
    UPDATE_FAILED = auto()

    def complete(self):
        '''
        Return the relative completed result code
        '''
        if self is UpdateResult.TO_CREATE:
            return UpdateResult.CREATED
        elif self is UpdateResult.TO_UPDATE:
            return UpdateResult.UPDATED
        else:
            return self

    def error(self):
        '''
        Return the relative error result code
        '''
        if self is UpdateResult.TO_CREATE:
            return UpdateResult.CREATE_FAILED
        elif self is UpdateResult.TO_UPDATE:
            return UpdateResult.UPDATE_FAILED
        elif self is UpdateResult.UNPACKING_OK:
            return UpdateResult.UNPACKING_FAILED
        else:
            return self
