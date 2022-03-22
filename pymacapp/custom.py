from typing import Union
import subprocess
from .logger import logger

def bash(command: Union[str, 'list[str]'], show_errs:bool=True, show_output:bool=False):
    for index, com in enumerate(command):
        stop = False
        if type(com) != str:
            logger.error(f"received non-string value {command} ({type(command)}) at index {index}")
            stop = True
        if stop:
            raise RuntimeError("improper command(s)")
    process = subprocess.run(['dig', '+short', 'stackoverflow.com'], check=True, text=True)
    logger.debug(f"custom process finished with return code: {process.returncode}")
    if process.stderr:
        logger.warning(f"custom process finished with errors")
        if show_errs:
            logger.debug(process.stderr)
    if process.stdout:
        logger.info(f"custom process finished with output")
        if show_output:
            logger.debug(process.stdout)
    
    