'''
Update results module
'''
from enum import IntEnum, auto
from yaam.utils.logger import static_logger as logger

from yaam.model.mutable.addon import Addon


class UpdateResult(IntEnum):
    '''
    Possible results of addon update
    '''
    NONE = 0

    # Advancement Status
    TO_INSTALL = auto()
    TO_UPDATE = auto()
    TO_UNPACK = auto()
    UP_TO_DATE = auto()

    # Ok
    INSTALLED = auto()
    UPDATED = auto()
    UNPACKED = auto()

    # ERRORS
    CREATE_FAILED = auto()
    UPDATE_FAILED = auto()
    UNPACKING_FAILED = auto()
    NO_UPDATE = auto()
    NO_METADATA = auto()
    INVALID_URL = auto()
    HTTP_REQUEST_FAILED = auto()
    DOWNLOAD_FAILED = auto()
    EMPTY_CONTENT = auto()
    INVALID_ZIP = auto()

    def complete(self):
        '''
        Return the relative completed result code
        '''
        if self is UpdateResult.TO_INSTALL:
            return UpdateResult.INSTALLED
        elif self is UpdateResult.TO_UPDATE:
            return UpdateResult.UPDATED
        elif self is UpdateResult.TO_UNPACK:
            return UpdateResult.UNPACKED
        else:
            return self

    def error(self):
        '''
        Return the relative error result code
        '''
        if self is UpdateResult.TO_INSTALL:
            return UpdateResult.CREATE_FAILED
        elif self is UpdateResult.TO_UPDATE:
            return UpdateResult.UPDATE_FAILED
        elif self is UpdateResult.UNPACKED:
            return UpdateResult.UNPACKING_FAILED
        else:
            return self

    def log_download(self, addon: Addon):
        '''
        Return prefetched log message and log level
        '''
        if self is UpdateResult.TO_INSTALL:
            logger().info(msg=f"Addon {addon.base.name} is not installed.")
        elif self is UpdateResult.TO_UPDATE:
            logger().info(msg=f"Avaliable updates detected for {addon.base.name}.")
        elif self is UpdateResult.UP_TO_DATE:
            logger().info(msg="No updates available.")
        elif self is UpdateResult.HTTP_REQUEST_FAILED:
            logger().error(msg=f"Communication error from {addon.base.uri}. Updates check will be skipped.")
        elif self is UpdateResult.EMPTY_CONTENT:
            logger().error(msg=f"Received empty content from {addon.base.uri}. Updates check will be skipped.")
        elif self is UpdateResult.NO_METADATA:
            logger().error(msg="Local or remote metadata are missing. Updates check will be skipped.")

    def log_update(self, addon: Addon):
        '''
        Return a default update message status
        '''
        filename = '...' if addon.binding.is_headless else addon.binding.path.name

        if self is UpdateResult.TO_INSTALL:
            logger().info(msg=f"Installing {addon.base.name}({filename})...")
        elif self is UpdateResult.INSTALLED:
            logger().info(msg=f"Installed {addon.base.name}({filename}).")
        elif self is UpdateResult.CREATE_FAILED:
            logger().error(msg=f"Failed to create {addon.base.name}({filename}).")
        elif self is UpdateResult.TO_UPDATE or self is UpdateResult.UP_TO_DATE:
            logger().info(msg=f"Updating {addon.base.name}({filename})...")
        elif self is UpdateResult.UPDATED:
            logger().info(msg=f"Updated {addon.base.name}({filename}).")
        elif self is UpdateResult.UPDATE_FAILED:
            logger().error(msg=f"Failed to update {addon.base.name}({filename}).")
        elif self is UpdateResult.TO_UNPACK:
            logger().info(msg=f"Unpacking {addon.base.name} updates to ({addon.binding.workspace})...")
        elif self is UpdateResult.UNPACKED:
            logger().info(msg=f"Unpacked {addon.base.name} updates to ({addon.binding.workspace}).")
        elif self is UpdateResult.UNPACKING_FAILED:
            logger().error(msg=f"Failed to unpack {addon.base.name} updates to ({addon.binding.workspace}).")
