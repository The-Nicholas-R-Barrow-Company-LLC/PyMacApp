import os
from .logger import logger

def spec(app_name:str, main_script:str, store_in:str=os.path.abspath(__file__), windowed:bool=True):
    
    if os.path.exists(main_script):
        if main_script[-3:] == ".py":
            _script_ = main_script
            logger.debug(f"set property _script_: ('{_script_}')")
        else:
            logger.error(f"'{main_script}' is not a python file")
            raise RuntimeError()
    else:
        logger.error(f"'{main_script}' does not exist")
        raise RuntimeError()

    if os.path.isdir(store_in):
        _directory_ = os.path.abspath(store_in)
        logger.debug(f"set property _directory_: '{_directory_}'")
    else:
        logger.warning(f"'{store_in}' is not a directory; defaulting to '{_directory_}'")
        _directory_ = os.path.abspath(__file__)
        logger.debug(f"set property _directory_: '{_directory_}'")


    command = ["pyi-makespec", "--name", _name_, "--windowed", "--specpath", _directory_, _script_]

if __name__ == "__main__":
    spec("this")