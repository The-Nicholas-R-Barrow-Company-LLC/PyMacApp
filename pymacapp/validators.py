import re
import os
from .logger import logger
from .helpers import APP_NAME_REGEX, BUNDLE_IDENTIFIER_REGEX, ARCHITECTURES, PYINSTALLER_LOG_LEVELS, MINIMUM_ENTITLEMENTS


def validate_version(version:list) -> bool:
    if len(version) == 0:
        logger.warning(f"invalid version: {version} (length == 0)")
        return False
    for index, item in enumerate(version):
        # logger.debug(f"{type(item)}: {type(item) == int}")
        if type(item) != int:
            logger.warning(f"invalid version: {version} (non-int value detected: index = {index}, value = {item})")
            return False
        elif item < 0:
            logger.warning(f"invalid version: {version} (<0 value int detected)")
            return False
    logger.info(f"validated: {version}")
    return True

def validate_app_name(name:str) -> bool:
    # App Name
    # Maximum Length: 50
    # Pattern: ^[0-9A-Za-z\d\s]+$
    if bool(re.fullmatch(APP_NAME_REGEX, name)) and len(name) <= 50:
        logger.info(f"validated: {name}")
        return True
    else:
        logger.warning(f"invalid app name: {name}")
        return False

def validate_identifier(identifier:str) -> bool:
    # Bundle Identifier
    # Maximum Length: 155
    # Pattern: ^[A-Za-z0-9\.\-]+$
    if bool(re.fullmatch(BUNDLE_IDENTIFIER_REGEX, identifier)) and len(identifier) <= 155:
        logger.info(f"validated: {identifier}")
        return True
    else:
        logger.warning(f"invalid bundle identifier: {identifier}")
        return False

def validate_directory(path:str) -> bool:
    if os.path.exists(path) and os.path.isdir(path):
        logger.info(f"validated: {path}")
        return True
    else:
        logger.warning(f"invalid directory: {path}")
        return False

def validate_file(path:str, type:str=None) -> bool:
    if os.path.exists(path) and os.path.isfile(path):
        if type:
            if path[-len(type):] == type:
                logger.info(f"validated: {path}")
                return True
            else:
                logger.warning(f"invalid file: {path}")
                return False
        else:
            logger.info(f"validated: {path}")
            return True
    else:
        logger.warning(f"invalid file: {path}")
        return False

def validate_pyinstaller_architecture(arch:str) -> bool:
    if arch in ARCHITECTURES:
        logger.info(f"validated: {arch}")
        return True
    else:
        logger.warning(f"invalid architecture: {arch}")
        return False

def validate_pyinstaller_log_level(level:str) -> bool:
    if level in PYINSTALLER_LOG_LEVELS:
        logger.info(f"validated: {level}")
        return True
    else:
        logger.warning(f"invalid log level: {level}")
        return False