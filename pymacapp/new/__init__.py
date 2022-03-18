from .logger import logger
import re, subprocess, os, time
from .helpers import make_spec, MINIMUM_ENTITLEMENTS

class App:

    def __init__(self, name:str, identifier:str=None) -> None:
        self.__name = name
        if self.__name[-4:] == ".app":
            logger.info(f"{name=} should not end in .app; this will be removed automatically ({self.__name} -> {self.__name[:-4]})")
            self.__name = self.__name[:-4]
        self.__identifier = identifier
        self.__main_script = None
        self.__spec = None
        self.__build = None
        self.__dist = None
        logger.debug(f"{self} created")

    def __repr__(self) -> str:
        return f"App({self.__name=})"

    def setup(self, script:str, overwrite=False):
        self.__main_script = script
        if not os.path.exists(self.__main_script):
            logger.error(f"{script=} does not exist")
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
        logger.info(f"build initiated")
        self.__build = build_path
        self.__dist = dist_path
        if not self.__spec:
            logger.error(f"'{self}.__spec' is currently None; call {self}.spec() to set this value")
        else:
            command = ["pyinstaller", "--noconfirm", "--distpath", f'{self.__dist}', "--workpath", f'{self.__build}', self.__spec]
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
    
    def sign(self, hash:str, entitlements:str=None):
        """sign an application

        :param hash: hash of an Application ID (Developer); use pymacapp.helpers.get_first_application_hash() to pull the default (see docs)
        :type hash: str
        :param entitlements: entitlements.plist file; use None for default/minimum file, defaults to None
        :type entitlements: str, optional
        :return: self (current app)
        :rtype: App
        """        
        APP = os.path.join(self.__dist, f"{self.__name}.app")
        __entitlements = ""
        __HASH = hash
        command = ["codesign", "--deep", "--force", "--timestamp", "--options", "runtime", "--entitlements", __entitlements, "--sign", __HASH, APP]
        if entitlements == None:
            logger.info(f"{entitlements=}, using default entitlements ({MINIMUM_ENTITLEMENTS=})")
            __entitlements = MINIMUM_ENTITLEMENTS
        elif os.path.exists(entitlements):
            __entitlements = entitlements
        else:
            logger.error(f"{entitlements=} does not exist")
        if not os.path.exists(APP):
            logger.error(f".app ('{APP}') does not exist")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=os.getcwd())
        output, error = process.communicate()
        if error:
            logger.warning(error)
        else:
            end = time.time()
            logger.info(f"sign completed")
        return self
        # """
        # #!/bin/bash
        # APPFILE='./dist/Italian Department.app'
        # codesign --deep --force --timestamp --options runtime --entitlements ./entitlements.plist --sign "CB05850DFD636ACF19E42F2BB4E5D81DD1068A6E" "$APPFILE"
        # # -f -s
        # # verify signature: 
        # echo "[sign-app] verifying signature" 
        # codesign --verify --verbose "$APPFILE"
        # # checks notary: spctl --assess --verbose $APPFILE
        # codesign -dvvv "$APPFILE"
        # """
        # must sign app, sign package seperately
        
    
    def all(self) -> None:
        return None

class Package:

    def __init__(self, app:App, identifier:str=None) -> None:
        self.app = app
        self.identifier = identifier
        logger.debug(f"{self} created")
    
    def __repr__(self) -> str:
        return f"Package({self.app=})"
    
    def build(self):
        return self

    def sign(self):
        return self
    
    def notorize(self):
        return self

    def wait(self):
        return self
    
    def staple(self):
        return self
    
    def all(self) -> None:
        return None