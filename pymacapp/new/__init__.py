from .logger import logger
import re, subprocess, os, time
from .helpers import make_spec

class App:

    def __init__(self, name:str, script:str, identifier:str=None) -> None:
        # if name == None or name == "":
        #     raise ValueError("App.name cannot be empty")
        # elif name[-4:] == ".app":
        #     logger.warning(f"{self}.name should not end in '.app'; the '.app' extension will be ignored")
        #     self.__name = name[:-4]
        # else:
        #     self.__name = name
        self.__name = name
        self.__identifier = identifier
        self.__main_script = script
        self.__spec = None
        self.__build = os.path.join(os.getcwd(), "build")
        self.__dist = os.path.join(os.getcwd(), "dist")
        logger.debug(f"{self} created")

    def __repr__(self) -> str:
        return f"App({self.__name=})"

    def spec(self, overwrite=False):
        parent_path = os.path.abspath(os.path.dirname(self.__main_script))
        file_path = os.path.join(parent_path, f"{self.__name}.spec")
        if os.path.exists(file_path):
            logger.info(f"'{file_path}' exists (delete to re-generate or set overwrite=True)")
            self.__spec = file_path
            if overwrite:
                logger.info(f"{overwrite=}, re-generating '{file_path}'")
                self.__spec = make_spec(self.__name, self.__identifier, self.__main_script, parent_path)
        else:
            logger.info(f"creating '{file_path}'")
            self.__spec = make_spec(self.__name, self.__identifier, self.__main_script, parent_path)
        return self
    
    def build(self, dist_path:str=os.path.join(os.getcwd(), "dist"), build_path:str=os.path.join(os.getcwd(), "build"), suppress_pyinstaller_output=True):
        start = time.time()
        if not self.__spec:
            logger.error(f"'{self}.__spec' is currently None; call {self}.spec() to set this value")
        else:
            command = ["pyinstaller", "--noconfirm", "--distpath", f'{dist_path}', "--workpath", f'{build_path}', self.__spec]
            if suppress_pyinstaller_output:
                command.insert(2, "--log-level")
                command.insert(3, "WARN")
            process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
            output, error = process.communicate()
            if error:
                logger.warning(error)
            else:
                end = time.time()
                logger.info(f"build completed in {round(end-start, 3)} seconds without errors detected")
        return self
    
    def sign(self):

        return self
