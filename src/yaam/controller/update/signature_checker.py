'''
Addon signature checker class module
'''

from typing import Tuple
from yaam.controller.update.results import UpdateResult
from yaam.model.mutable.addon import Addon
from yaam.model.mutable.metadata import AddonMetadata
from yaam.utils.hashing import Hasher
from yaam.utils.logger import static_logger as logger


class SignatureChecker(object):
    '''
    Addon signature checker class
    '''

    @staticmethod
    def check_signatures(content: bytes, addon: Addon, metadata: AddonMetadata) -> Tuple[UpdateResult, str]:
        '''
        Check the hash signature of the given bytes content with the one specified in the addon metadata
        '''

        ret_code = UpdateResult.TO_CREATE
        remote_signature = Hasher.SHA256.make_hash_from_bytes(content)

        if addon.binding.path.exists():
            logger().info(msg=f"Checking {addon.base.name}({addon.binding.path.name}) hash signatures...")

            if len(metadata.hash_signature) > 0:
                logger().info(msg=f"Local signature is {metadata.hash_signature}.")
                logger().info(msg=f"Remote signature is {remote_signature}.")

                if remote_signature == metadata.hash_signature:
                    logger().info(msg=f"Addon {addon.base.name} is up-to-date.")
                    ret_code = UpdateResult.UP_TO_DATE
                else:
                    logger().info(msg="New addon update found. Updating...")
                    ret_code = UpdateResult.TO_UPDATE
            else:
                logger().info(msg="Local signature is missing. Updating...")
                ret_code = UpdateResult.TO_UPDATE
        else:
            logger().info(msg=f"Addon {addon.base.name}({addon.binding.path.name}) missing...")

        return (ret_code, remote_signature)
