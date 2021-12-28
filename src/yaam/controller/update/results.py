'''
Update results module
'''
from enum import IntEnum, auto

from yaam.model.mutable.addon import Addon

class UpdateResult(IntEnum):
    '''
    Possible results of addon update
    '''
    NONE = 0

    # OK
    TO_CREATE = auto()
    TO_UPDATE = auto()
    UP_TO_DATE = auto()
    TO_UNPACK = auto()
    UNPACKING_OK = auto()
    CREATED = auto()
    UPDATED = auto()
    UPDATE_METADATA = auto()

    # ERRORS
    INVALID_URL = auto()
    DOWNLOAD_FAILED = auto()
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

    def message(self, addon: Addon) -> str:
        '''
        Return a default update message status
        '''
        filename = '...' if addon.binding.is_headless else addon.binding.path.name
        if self is UpdateResult.TO_CREATE:
            return f"Creating {addon.base.name}({filename})..."
        elif self is UpdateResult.CREATED:
            return f"Created {addon.base.name}({filename})."
        elif self is UpdateResult.CREATE_FAILED:
            return f"Failed to create {addon.base.name}({filename})."
        elif self is UpdateResult.TO_UPDATE:
            return f"Updating {addon.base.name}({filename})..."
        elif self is UpdateResult.UPDATED:
            return f"Updated {addon.base.name}({filename})."
        elif self is UpdateResult.UPDATE_FAILED:
            return f"Failed to update {addon.base.name}({filename})."
        else:
            return ''
