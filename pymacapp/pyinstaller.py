from .logger import logger
from .exceptions import BuildException
from .validators import validate_app_name, validate_directory, validate_file,  validate_identifier, validate_pyinstaller_architecture, validate_pyinstaller_log_level
from .helpers import ARCHITECTURES, PYINSTALLER_LOG_LEVELS
from .command import Command, cmd
import os
from dataclasses import dataclass
"""
Full list of needed commands (remember to separate with spaces)
pyi-makespec 
--name NAME
--icon {icon} 
--osx-bundle-identifier BUNDLE_IDENTIFIER
--target-architecture {ARCH: x86_64, arm64, or universal2}
--osx-entitlements-file FILENAME
--hidden-import MODULENAME
--add-data <SRC;DEST or SRC:DEST> {this option can be used multiple times}
--specpath {DIR: directory to store specpath, default to pymacapp/__file__)}
--log-level {LEVEL: TRACE, DEBUG, INFO, WARN, ERROR, CRITICAL}
{main.py}
"""
@dataclass(frozen=True, repr=True)
class Data:
    """create an object to add non-python files during the build process. NOTE: if the src and dest should be the same, the included files will need different paths when used in your code.

    :param src: the file or directory to include in the built app-bundle
    :type src: str
    :param dest: where to put the src content in the built app-bundle (use '.' for root)
    :type dest: str
    """
    src:str
    dest:str

def spec(name:str, 
        main_script:str, 
        icon:str=None, 
        identifier:str=None, 
        architecture:str="universal2", 
        entitlements:str=None, 
        # hidden_imports:"list[str]"=None,
        # add_data:"list[Data]"=None,
        specpath:str=os.path.abspath(os.path.dirname(__file__)),
        log_level:str = "INFO",
        brute:bool = False):
    command = "pyi-makespec"

    if not validate_app_name(name):
        if not brute:
            raise BuildException(f"unable to validate {name=}")
    
    if not validate_file(main_script, ".py"):
        if not brute:
            raise BuildException(f"unable to validate {main_script=}")

    if icon:
        if validate_file(icon):
            command += f" --icon '{icon}'"
            logger.debug(f"adding --icon f'{icon}'")
        else:
            if not brute:
                raise BuildException(f"unable to validate {icon=}")
            else:
                command += f" --icon '{icon}'"
                logger.debug(f"adding --icon f'{icon}'")
    
    if identifier:
        if validate_identifier(identifier):
            command += f" --osx-bundle-identifier {identifier}"
            logger.debug(f"adding: --osx-bundle-identifier {identifier}")
        else:
            if not brute:
                raise BuildException(f"unable to validate {identifier=}")
            else:
                command += f" --osx-bundle-identifier {identifier}"
                logger.debug(f"adding: --osx-bundle-identifier {identifier}")
    
    if architecture:
        if validate_pyinstaller_architecture(architecture):
            command += f" --target-architecture {architecture}"
            logger.debug(f"adding: --target-architecture {architecture}")
        else:
            raise BuildException(f"unable to validate {architecture=}; must be one of {ARCHITECTURES} (will not be ignored by brute=True)")

    if entitlements:
        if validate_file(entitlements, ".plist"):
            command += f" --osx-entitlements-file '{entitlements}'"
            logger.debug(f"adding --osx-entitlements-file '{entitlements}'")
        else:
            if not brute:
                raise BuildException(f"unable to validate {entitlements=}")
            else:
                command += f" --osx-entitlements-file '{entitlements}'"
                logger.debug(f"adding --osx-entitlements-file '{entitlements}'")

    if specpath:
        if validate_directory(specpath):
            command += f" --specpath '{specpath}'"
            logger.debug(f"adding --specpath '{specpath}'")
        else:
            if not brute:
                raise BuildException(f"unable to validate {specpath=}")
            else:
                command += f" --specpath '{specpath}'"
                logger.debug(f"adding --specpath '{specpath}'")

    if log_level:
        if validate_pyinstaller_log_level(log_level):
            command += f" --log-level {log_level}"
            logger.debug(f"adding: --log-level {log_level}")
        else:
            raise BuildException(f"unable to validate {log_level=}; must be one of {PYINSTALLER_LOG_LEVELS} (will not be ignored by brute=True)")

    command += f" '{main_script}'"

    resp:Command = cmd(command)

    for line in resp.output.splitlines():
        if "Wrote " in line:
            return line[6:-1]

